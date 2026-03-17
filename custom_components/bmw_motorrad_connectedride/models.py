from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def _ts_to_dt(value: int | float | None) -> datetime | None:
    if value in (None, 0):
        return None
    if value > 10_000_000_000:
        value = value / 1000
    return datetime.fromtimestamp(value, tz=timezone.utc)


def _div_1000(value: int | float | None) -> float | None:
    if value in (None, 0):
        return 0.0 if value == 0 else None
    return round(float(value) / 1000, 3)


@dataclass(slots=True)
class BikeData:
    bike_id: str
    name: str | None
    vin: str | None
    type_key: str | None
    color: str | None
    fuel_level: int | float | None
    energy_level: int | float | None
    remaining_range_km: float | None
    remaining_range_electric_km: float | None
    total_mileage_km: float | None
    trip1_km: float | None
    total_connected_distance_km: float | None
    next_service_remaining_distance_km: float | None
    tire_pressure_front_bar: float | None
    tire_pressure_rear_bar: float | None
    next_service_due_date: datetime | None
    last_connected_time: datetime | None
    last_activated_time: datetime | None
    latitude: float | None
    longitude: float | None
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "BikeData":
        bike_id = str(
            data.get("itemId")
            or data.get("vehicleId")
            or data.get("vin")
            or data.get("hashedShortVin")
            or data.get("typeKey")
            or "motorrad"
        )

        return cls(
            bike_id=bike_id,
            name=data.get("name"),
            vin=data.get("vin"),
            type_key=data.get("typeKey"),
            color=data.get("color"),
            fuel_level=data.get("fuelLevel"),
            energy_level=data.get("energyLevel"),
            remaining_range_km=_div_1000(data.get("remainingRange")),
            remaining_range_electric_km=_div_1000(data.get("remainingRangeElectric")),
            total_mileage_km=_div_1000(data.get("totalMileage")),
            trip1_km=_div_1000(data.get("trip1")),
            total_connected_distance_km=_div_1000(data.get("totalConnectedDistance")),
            next_service_remaining_distance_km=_div_1000(data.get("nextServiceRemainingDistance")),
            tire_pressure_front_bar=data.get("tirePressureFront"),
            tire_pressure_rear_bar=data.get("tirePressureRear"),
            next_service_due_date=_ts_to_dt(data.get("nextServiceDueDate")),
            last_connected_time=_ts_to_dt(data.get("lastConnectedTime")),
            last_activated_time=_ts_to_dt(data.get("lastActivatedTime")),
            latitude=data.get("lastConnectedLat"),
            longitude=data.get("lastConnectedLon"),
            raw=data,
        )
