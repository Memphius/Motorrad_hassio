from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def _ts_to_dt(value: int | float | None) -> datetime | None:
    if value in (None, 0):
        return None
    # BMW payloads appear to use ms epoch in some places.
    if value > 10_000_000_000:
        value = value / 1000
    return datetime.fromtimestamp(value, tz=timezone.utc)


@dataclass(slots=True)
class BikeData:
    bike_id: str
    type_key: str | None
    color: str | None
    fuel_level: int | float | None
    remaining_range_km: int | float | None
    total_mileage_km: int | float | None
    trip1_km: int | float | None
    tire_pressure_front_bar: float | None
    tire_pressure_rear_bar: float | None
    next_service_due_date: datetime | None
    next_service_remaining_distance_km: int | float | None
    last_connected_time: datetime | None
    last_activated_time: datetime | None
    latitude: float | None
    longitude: float | None
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "BikeData":
        bike_id = str(data.get("id") or data.get("vin") or data.get("typeKey") or "motorrad")
        return cls(
            bike_id=bike_id,
            type_key=data.get("typeKey"),
            color=data.get("color"),
            fuel_level=data.get("fuelLevel"),
            remaining_range_km=data.get("remainingRange"),
            total_mileage_km=data.get("totalMileage"),
            trip1_km=data.get("trip1"),
            tire_pressure_front_bar=data.get("tirePressureFront"),
            tire_pressure_rear_bar=data.get("tirePressureRear"),
            next_service_due_date=_ts_to_dt(data.get("nextServiceDueDate")),
            next_service_remaining_distance_km=data.get("nextServiceRemainingDistance"),
            last_connected_time=_ts_to_dt(data.get("lastConnectedTime")),
            last_activated_time=_ts_to_dt(data.get("lastActivatedTime")),
            latitude=data.get("lastConnectedLat"),
            longitude=data.get("lastConnectedLon"),
            raw=data,
        )
