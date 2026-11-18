"""Pydantic models. Fields use English names; ATM's (Italian) names are accepted as aliases."""

from __future__ import annotations

from enum import IntEnum, StrEnum
from typing import Annotated, Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class _Model(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")


def _nonzero(v: Any) -> Any:
    return None if v in (0, 0.0, -1, "", None) else v


Latitude = Annotated[float, Field(ge=-90, le=90, description="WGS84 latitude")]
Longitude = Annotated[float, Field(ge=-180, le=180, description="WGS84 longitude")]


class PlaceKind(StrEnum):
    ADDRESS = "INDIRIZZO"
    LOCALITY = "LOCALITA"
    POI = "POI"


class TransportMode(StrEnum):
    METRO = "Metro"
    BUS = "Bus"
    TRAM = "Tram"
    RAIL = "Rail"


class Place(_Model):
    """A search result: address, locality or point of interest (incl. stations)."""

    id: int = Field(validation_alias=AliasChoices("Id", "id"))
    kind: PlaceKind = Field(validation_alias=AliasChoices("Tipo", "kind"))
    name: str = Field(validation_alias=AliasChoices("Nome", "name"))
    municipality: str = Field("", validation_alias=AliasChoices("Comune", "municipality"))
    address: str | None = Field(None, validation_alias=AliasChoices("Indirizzo", "address"))
    category: str | None = Field(None, validation_alias=AliasChoices("Categoria", "category"))
    code: str | None = Field(
        None,
        validation_alias=AliasChoices("CodicePOI", "code"),
        description="Stop/POI code when available (usable with stop tools)",
    )
    house_number: str | None = Field(None, validation_alias=AliasChoices("Civico", "house_number"))
    lat: Latitude | None = Field(None, validation_alias=AliasChoices("Lat", "lat"))
    lng: Longitude | None = Field(None, validation_alias=AliasChoices("Lng", "lng"))

    @model_validator(mode="before")
    @classmethod
    def _zero_coords_are_missing(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data = dict(data)
            for key in ("Lat", "Lng"):
                if key in data:
                    data[key] = _nonzero(data[key])
            for key in ("Civico", "CodicePOI", "Categoria", "Indirizzo"):
                if data.get(key) == "":
                    data[key] = None
        return data

    @property
    def description(self) -> str:
        return f"{self.name}, {self.municipality}" if self.municipality else self.name

    @property
    def has_coordinates(self) -> bool:
        return self.lat is not None and self.lng is not None


class SearchResults(_Model):
    places: list[Place]
    total_pages: int = 1
    total_records: int = 0


class Waypoint(_Model):
    """A point on a trip (origin, destination, or a transit stop)."""

    name: str = Field(validation_alias=AliasChoices("Description", "name"))
    code: str | None = Field(None, validation_alias=AliasChoices("Code", "code"))
    lat: Latitude
    lng: Longitude

    @model_validator(mode="before")
    @classmethod
    def _flatten(cls, data: Any) -> Any:
        if isinstance(data, dict) and isinstance(data.get("Location"), dict):
            data = {**data, "lat": data["Location"]["Y"], "lng": data["Location"]["X"]}
            if data.get("Code") == "":
                data["Code"] = None
        return data


class StepType(IntEnum):
    DEPART = 0
    WALK = 1
    RIDE = 2
    ARRIVE = 3
    BOARD_STOP = 4
    ALIGHT_STOP = 5


class Ride(_Model):
    """One candidate line serving a ride leg."""

    line_code: str
    line_description: str
    direction: str
    journey_pattern_id: str
    frequency_minutes: int | None = None
    stops_on_board: int | None = None

    @model_validator(mode="before")
    @classmethod
    def _flatten(cls, data: Any) -> Any:
        if isinstance(data, dict) and "JourneyPattern" in data:
            jp = data["JourneyPattern"]
            return {
                "line_code": jp["Line"]["LineCode"],
                "line_description": jp["Line"]["LineDescription"],
                "direction": jp["Direction"],
                "journey_pattern_id": jp["Id"],
                "frequency_minutes": _nonzero(data.get("Frequence")),
                "stops_on_board": data.get("OnBoardStops"),
            }
        return data


class TripStep(_Model):
    order: int = Field(validation_alias=AliasChoices("ActionOrder", "order"))
    type: StepType = Field(validation_alias=AliasChoices("ActionType", "type"))
    description: str = Field(validation_alias=AliasChoices("ActionDescription", "description"))
    place: Waypoint | None = Field(None, validation_alias=AliasChoices("Place", "place"))
    length_m: int | None = None
    rides: list[Ride] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _flatten(cls, data: Any) -> Any:
        if isinstance(data, dict) and isinstance(data.get("Leg"), dict):
            leg = data["Leg"]
            data = {
                **data,
                "length_m": leg.get("Length"),
                "rides": leg.get("Journeys") or [],
            }
        return data


class Fare(_Model):
    description: str = Field(validation_alias=AliasChoices("Description", "description"))
    price_eur: float = Field(validation_alias=AliasChoices("Price", "price_eur"))
    zone: str | None = Field(None, validation_alias=AliasChoices("DescriptionZone", "zone"))
    url: str | None = Field(None, validation_alias=AliasChoices("Url", "url"))


class Trip(_Model):
    id: str = Field(validation_alias=AliasChoices("TripId", "id"))
    number: int = Field(validation_alias=AliasChoices("TripNumber", "number"))
    duration_minutes: int = Field(
        validation_alias=AliasChoices("TotalDuration", "duration_minutes")
    )
    total_length_m: int = Field(validation_alias=AliasChoices("TotalLength", "total_length_m"))
    walking_length_m: int = Field(
        validation_alias=AliasChoices("WalkingLength", "walking_length_m")
    )
    steps: list[TripStep] = Field(validation_alias=AliasChoices("Actions", "steps"))
    fare: Fare | None = Field(None, validation_alias=AliasChoices("Tariff", "fare"))
    has_traffic_alerts: bool = False
    info_message: str | None = Field(
        None, validation_alias=AliasChoices("InfoMessage", "info_message")
    )

    @model_validator(mode="before")
    @classmethod
    def _alerts(cls, data: Any) -> Any:
        if isinstance(data, dict) and "JPsWithTrafficInfos" in data:
            data = {**data, "has_traffic_alerts": bool(data["JPsWithTrafficInfos"])}
            if data.get("InfoMessage") == "":
                data["InfoMessage"] = None
        return data


class TripPlan(_Model):
    origin: Place | None = None
    destination: Place | None = None
    trips: list[Trip]


class LineStop(_Model):
    code: str = Field(validation_alias=AliasChoices("Code", "code"))
    name: str = Field(validation_alias=AliasChoices("Description", "name"))
    lat: Latitude
    lng: Longitude

    @model_validator(mode="before")
    @classmethod
    def _flatten(cls, data: Any) -> Any:
        if isinstance(data, dict) and isinstance(data.get("Location"), dict):
            data = {**data, "lat": data["Location"]["Y"], "lng": data["Location"]["X"]}
        return data


class LineRoute(_Model):
    """Ordered stops of one line in one direction."""

    id: str = Field(validation_alias=AliasChoices("Id", "id"))
    line_code: str
    direction: str = Field(validation_alias=AliasChoices("Direction", "direction"))
    description: str
    stops: list[LineStop] = Field(validation_alias=AliasChoices("Stops", "stops"))

    @model_validator(mode="before")
    @classmethod
    def _flatten(cls, data: Any) -> Any:
        if isinstance(data, dict) and "Line" in data:
            data = {
                **data,
                "line_code": data["Line"]["LineCode"],
                "description": data["Line"]["LineDescription"],
            }
        return data


class StopArrival(_Model):
    """A line serving a stop, with the live wait message (e.g. '5 min')."""

    line_code: str
    line_description: str
    direction: str
    journey_pattern_id: str
    wait: str | None = None
    has_traffic_alerts: bool = False

    @model_validator(mode="before")
    @classmethod
    def _flatten(cls, data: Any) -> Any:
        if isinstance(data, dict) and "Line" in data:
            return {
                "line_code": data["Line"]["LineCode"],
                "line_description": data["Line"]["LineDescription"],
                "direction": data["Direction"],
                "journey_pattern_id": data["JourneyPatternId"],
                "wait": data.get("WaitMessage") or None,
                "has_traffic_alerts": bool(data.get("TrafficBulletins")),
            }
        return data


class StopLines(_Model):
    stop_code: str
    stop_name: str
    lat: Latitude
    lng: Longitude
    arrivals: list[StopArrival]

    @model_validator(mode="before")
    @classmethod
    def _flatten(cls, data: Any) -> Any:
        if isinstance(data, dict) and "StopPoint" in data:
            sp = data["StopPoint"]
            return {
                "stop_code": sp["Code"],
                "stop_name": sp["Description"],
                "lat": sp["Location"]["Y"],
                "lng": sp["Location"]["X"],
                "arrivals": data.get("Lines", []),
            }
        return data


class HourSlot(_Model):
    hour: int = Field(validation_alias=AliasChoices("Hour", "hour"))
    minutes: str = Field(
        "",
        validation_alias=AliasChoices("ScheduleDetail", "minutes"),
        description="Raw minute list, e.g. '32 44 54'; '*' marks variants; may be 'Ogni 7' ...'",
    )


class DaySchedule(_Model):
    day_type: str
    days: list[str]
    slots: list[HourSlot]

    @model_validator(mode="before")
    @classmethod
    def _flatten(cls, data: Any) -> Any:
        if isinstance(data, dict) and "DayType" in data:
            dt = data["DayType"]
            names = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Hol")
            return {
                "day_type": dt["DayTypeDescription"],
                "days": [n for n in names if dt.get(n)],
                "slots": [
                    {**s, "ScheduleDetail": (s.get("ScheduleDetail") or "").strip()}
                    for s in data.get("Schedule", [])
                ],
            }
        return data


class Timetable(_Model):
    stop_code: str = Field(validation_alias=AliasChoices("StopCode", "stop_code"))
    line_code: str = Field(validation_alias=AliasChoices("LineCode", "line_code"))
    direction: str = Field(validation_alias=AliasChoices("Direction", "direction"))
    valid_from: str | None = Field(None, validation_alias=AliasChoices("DescOrario", "valid_from"))
    schedules: list[DaySchedule] = Field(
        validation_alias=AliasChoices("TimeSchedules", "schedules")
    )


class MetroStation(_Model):
    name: str
    lines: list[str]
    lat: Latitude
    lng: Longitude
