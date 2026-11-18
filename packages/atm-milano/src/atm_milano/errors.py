# Copyright (C) 2026 Matteo Redaelli
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Exception hierarchy."""


class AtmError(Exception):
    """Base class for all errors raised by this library."""


class AtmBlockedError(AtmError):
    """The edge/bot protection (Akamai) rejected the request (HTTP 403)."""


class AtmNotFoundError(AtmError):
    """The requested resource (line, stop, place) does not exist."""


class AtmApiError(AtmError):
    """The upstream service returned an unexpected status or payload."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
