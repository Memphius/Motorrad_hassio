from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import BMWMotorradEntity
from .models import BikeData


@dataclass(frozen=True, kw_only=True)
class BMWMotorradBinarySensorDescription(BinarySensorEntityDescription):
    value_fn: Callable[[BikeData], bool]


BINARY_SENSORS: tuple[BMWMotorradBinarySensorDescription, ...] = (
    BMWMotorradBinarySensorDescription(
        key="low_fuel",
        translation_key="low_fuel",
        value_fn=lambda bike: (bike.fuel_level or 0) <= 20,
    ),
    BMWMotorradBinarySensorDescription(
        key="front_tire_pressure_low",
        translation_key="front_tire_pressure_low",
        value_fn=lambda bike: (bike.tire_pressure_front_bar or 0) < 2.0,
    ),
    BMWMotorradBinarySensorDescription(
        key="rear_tire_pressure_low",
        translation_key="rear_tire_pressure_low",
        value_fn=lambda bike: (bike.tire_pressure_rear_bar or 0) < 2.3,
    ),
    BMWMotorradBinarySensorDescription(
        key="service_due_soon",
        translation_key="service_due_soon",
        value_fn=lambda bike: (bike.next_service_remaining_distance_km or 999999) < 1000,
    ),
)


class BMWMotorradBinarySensor(BMWMotorradEntity, BinarySensorEntity):
    entity_description: BMWMotorradBinarySensorDescription

    def __init__(self, coordinator, bike_id: str, description: BMWMotorradBinarySensorDescription) -> None:
        super().__init__(coordinator, bike_id)
        self.entity_description = description
        self._attr_unique_id = f"{bike_id}_{description.key}"

    @property
    def is_on(self) -> bool:
        return self.entity_description.value_fn(self.bike)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = entry.runtime_data.coordinator
    entities: list[BinarySensorEntity] = []
    for bike_id in coordinator.data:
        for description in BINARY_SENSORS:
            entities.append(BMWMotorradBinarySensor(coordinator, bike_id, description))
    async_add_entities(entities)
