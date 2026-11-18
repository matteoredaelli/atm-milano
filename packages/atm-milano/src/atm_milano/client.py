"""Async HTTP client for ATM Milano (GiroMilano) and the Comune di Milano GIS."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable
from datetime import datetime
from types import TracebackType
from typing import Any, Literal, Protocol, Self
from zoneinfo import ZoneInfo

from curl_cffi import requests as cffi

from .errors import AtmApiError, AtmBlockedError, AtmNotFoundError
from .models import (
    LineRoute,
    MetroStation,
    Place,
    PlaceKind,
    SearchResults,
    StopLines,
    Timetable,
    TransportMode,
    Trip,
    TripPlan,
)

BASE = "https://giromilano.atm.it"
SEARCH_API = f"{BASE}/proxy.search/api/atmSearch"
TP_API = f"{BASE}/proxy.tpportal/api/tpportal"
GIS_METRO = (
    "https://gisportal.comune.milano.it/server/rest/services/D_Mobilita/ATM_Metro/MapServer/0/query"
)
ROME = ZoneInfo("Europe/Rome")

Lang = Literal["en", "it"]
PlaceRef = str | Place | tuple[float, float]
"""A free-text query, a resolved Place, or a (lat, lng) tuple."""


class HttpSession(Protocol):
    """The subset of curl_cffi's AsyncSession used here (lets tests inject a fake)."""

    async def request(self, method: str, url: str, **kwargs: Any) -> Any: ...
    async def close(self) -> Any: ...


class AtmClient:
    """Client for the unofficial GiroMilano endpoints.

    Uses Chrome TLS impersonation (curl_cffi) because the site sits behind Akamai bot protection.
    """

    def __init__(
        self,
        *,
        lang: Lang = "en",
        timeout: float = 20.0,
        retries: int = 2,
        session: HttpSession | None = None,
    ) -> None:
        self.lang: Lang = lang
        self.timeout = timeout
        self.retries = retries
        self._owns_session = session is None
        self._session: HttpSession = session or cffi.AsyncSession(  # ty: ignore[invalid-assignment]
            impersonate="chrome",
            headers={"Referer": f"{BASE}/", "Accept": "application/json, text/plain, */*"},
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_session:
            await self._session.close()

    # -- transport ---------------------------------------------------------------------------

    async def _request(self, method: str, url: str, params: dict[str, Any] | None = None) -> Any:
        last: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                r = await self._session.request(method, url, params=params, timeout=self.timeout)
            except Exception as e:  # network-level failure
                last = AtmApiError(f"{method} {url} failed: {e}")
            else:
                if r.status_code == 403:
                    raise AtmBlockedError(f"Blocked by edge protection: {url}")
                if r.status_code == 404:
                    raise AtmNotFoundError(f"Not found: {url}")
                if r.status_code < 400:
                    try:
                        return r.json()
                    except ValueError as e:
                        raise AtmApiError(f"Invalid JSON from {url}", r.status_code) from e
                last = AtmApiError(f"HTTP {r.status_code} from {url}", r.status_code)
                if r.status_code < 500:
                    raise last
            if attempt < self.retries:
                await asyncio.sleep(0.5 * 2**attempt)
        assert last is not None
        raise last

    # -- places ------------------------------------------------------------------------------

    async def search_places(
        self,
        term: str,
        *,
        kinds: Iterable[PlaceKind] = (PlaceKind.ADDRESS, PlaceKind.LOCALITY, PlaceKind.POI),
        limit: int = 15,
        lang: Lang | None = None,
    ) -> SearchResults:
        """Search addresses, localities and POIs (stations, stops, bike-sharing...)."""
        data = await self._request(
            "GET",
            f"{SEARCH_API}/search",
            {
                "Lang": lang or self.lang,
                "RighePerCategoria": 3,
                "Tipi": ",".join(k.value for k in kinds),
                "page": 1,
                "rows": limit,
                "soloGeocodificati": "true",
                "searchTerm": term,
            },
        )
        return SearchResults(
            places=[Place.model_validate(r) for r in data.get("rows", [])],
            total_pages=int(data.get("total", 1) or 1),
            total_records=int(data.get("records", 0) or 0),
        )

    async def geocode(self, place: Place) -> Place:
        """Fill in coordinates for an address result that lacks them."""
        if place.has_coordinates:
            return place
        data = await self._request(
            "POST",
            f"{SEARCH_API}/Geocode",
            {
                "comune": place.municipality,
                "indirizzo": place.name,
                "civico": place.house_number or "",
            },
        )
        item = data.get("geocodeditem")
        if not item:
            raise AtmNotFoundError(f"Could not geocode {place.description!r}")
        lat = item["lat"] if item.get("lat", -1) != -1 else item.get("p_lat")
        lng = item["lon"] if item.get("lon", -1) != -1 else item.get("p_lon")
        if lat is None or lng is None:
            raise AtmNotFoundError(f"Could not geocode {place.description!r}")
        return place.model_copy(update={"lat": lat, "lng": lng})

    async def resolve_place(self, ref: PlaceRef) -> Place:
        """Turn a text query / Place / (lat, lng) into a Place with coordinates."""
        if isinstance(ref, tuple):
            lat, lng = ref
            return Place(
                id=0, kind=PlaceKind.ADDRESS, name=f"{lat:.5f},{lng:.5f}", lat=lat, lng=lng
            )
        if isinstance(ref, Place):
            return await self.geocode(ref)
        results = await self.search_places(ref, limit=5)
        if not results.places:
            raise AtmNotFoundError(f"No place found for {ref!r}")
        # Prefer a POI (stations etc.) or Milan address that already has coordinates.
        ranked = sorted(
            results.places,
            key=lambda p: (p.municipality.lower() != "milano", not p.has_coordinates),
        )
        return await self.geocode(ranked[0])

    # -- trips -------------------------------------------------------------------------------

    async def plan_trip(
        self,
        origin: PlaceRef,
        destination: PlaceRef,
        *,
        when: datetime | None = None,
        modes: Iterable[TransportMode] = (
            TransportMode.METRO,
            TransportMode.BUS,
            TransportMode.TRAM,
            TransportMode.RAIL,
        ),
        lang: Lang | None = None,
    ) -> TripPlan:
        """Plan public-transport trips departing at `when` (default: now, Europe/Rome)."""
        src, dst = await asyncio.gather(self.resolve_place(origin), self.resolve_place(destination))
        if when is None:
            when = datetime.now(ROME)
        elif when.tzinfo is None:
            when = when.replace(tzinfo=ROME)
        else:
            when = when.astimezone(ROME)
        data = await self._request(
            "GET",
            f"{TP_API}/tpl/trips",
            {
                "FromPoint.X": src.lng,
                "FromPoint.Y": src.lat,
                "ToPoint.X": dst.lng,
                "ToPoint.Y": dst.lat,
                "Date": when.strftime("%Y-%m-%d"),
                "FromSeconds": when.hour * 3600 + when.minute * 60,
                "TransportModes": ",".join(m.value for m in modes),
                "Lang": lang or self.lang,
                "FromDescription": src.description,
                "ToDescription": dst.description,
            },
        )
        return TripPlan(
            origin=src,
            destination=dst,
            trips=[Trip.model_validate(t) for t in data.get("Trips") or []],
        )

    # -- lines & stops -----------------------------------------------------------------------

    async def get_line_route(self, line_code: str, direction: int = 0) -> LineRoute:
        """Ordered stops of a line. Metro codes are -1..-5 (M1..M5); bus/tram use their number."""
        line_code = _normalize_line(line_code)
        data = await self._request(
            "GET",
            f"{TP_API}/tpl/journeyPatterns/{line_code}|{direction}",
            {"alternativeRoutesMode": "false"},
        )
        return LineRoute.model_validate(data)

    async def get_stop_lines(self, stop_code: str) -> StopLines:
        """Lines serving a stop, with live wait messages."""
        data = await self._request("GET", f"{TP_API}/tpl/stops/{stop_code}/linesummary")
        return StopLines.model_validate(data)

    async def get_stop_timetable(
        self, stop_code: str, line_code: str, direction: int = 0
    ) -> Timetable:
        """Scheduled timetable of a line at a stop."""
        line_code = _normalize_line(line_code)
        data = await self._request(
            "GET", f"{TP_API}/tpl/stops/{stop_code}/timetable/line/{line_code}/dir/{direction}"
        )
        return Timetable.model_validate(data)

    # -- metro (Comune di Milano GIS) --------------------------------------------------------

    async def list_metro_stations(self, line: str | None = None) -> list[MetroStation]:
        """All metro station entries (one per line served) from the Comune di Milano GIS."""
        out: list[MetroStation] = []
        offset = 0
        while True:
            data = await self._request(
                "GET",
                GIS_METRO,
                {
                    "where": "1=1",
                    "outFields": "linee,nome",
                    "returnGeometry": "true",
                    "outSR": 4326,
                    "f": "json",
                    "resultOffset": offset,
                    "resultRecordCount": 1000,
                },
            )
            feats = data.get("features", [])
            for f in feats:
                g, a = f.get("geometry"), f["attributes"]
                if not g:
                    continue
                out.append(
                    MetroStation(
                        name=a["nome"],
                        lines=[x.strip() for x in str(a["linee"]).split(",") if x.strip()],
                        lat=g["y"],
                        lng=g["x"],
                    )
                )
            if not data.get("exceededTransferLimit") or not feats:
                break
            offset += len(feats)
        if line:
            want = line.upper().removeprefix("M")
            out = [s for s in out if want in s.lines]
        return out


_METRO_CODES = {"M1": "-1", "M2": "-2", "M3": "-3", "M4": "-4", "M5": "-5"}


def _normalize_line(code: str) -> str:
    """Accept 'M1'..'M5' as aliases of the internal negative codes."""
    return _METRO_CODES.get(code.strip().upper(), code.strip())
