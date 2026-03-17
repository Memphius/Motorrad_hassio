from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfLength, UnitOfPressure, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import BMWMotorradEntity
from .models import BikeData


@dataclass(frozen=True, kw_only=True)
class BMWMotorradSensorDescription(SensorEntityDescription):
    value_fn: Callable[[BikeData], object]


SENSORS: tuple[BMWMotorradSensorDescription, ...] = (
    BMWMotorradSensorDescription(
        key="fuel_level",
        translation_key="fuel_level",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda bike: bike.fuel_level,
    ),
    BMWMotorradSensorDescription(
        key="remaining_range",
        translation_key="remaining_range",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda bike: bike.remaining_range_km,
    ),
    BMWMotorradSensorDescription(
        key="total_mileage",
        translation_key="total_mileage",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda bike: bike.total_mileage_km,
    ),
    BMWMotorradSensorDescription(
        key="trip1",
        translation_key="trip1",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda bike: bike.trip1_km,
    ),
    BMWMotorradSensorDescription(
        key="tire_pressure_front",
        translation_key="tire_pressure_front",
        native_unit_of_measurement=UnitOfPressure.BAR,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda bike: bike.tire_pressure_front_bar,
    ),
    BMWMotorradSensorDescription(
        key="tire_pressure_rear",
        translation_key="tire_pressure_rear",
        native_unit_of_measurement=UnitOfPressure.BAR,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda bike: bike.tire_pressure_rear_bar,
    ),
    BMWMotorradSensorDescription(
        key="next_service_due_date",
        translation_key="next_service_due_date",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda bike: bike.next_service_due_date,
    ),
    BMWMotorradSensorDescription(
        key="next_service_remaining_distance",
        translation_key="next_service_remaining_distance",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda bike: bike.next_service_remaining_distance_km,
    ),
    BMWMotorradSensorDescription(
        key="last_connected_time",
        translation_key="last_connected_time",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda bike: bike.last_connected_time,
    ),
    BMWMotorradSensorDescription(
        key="last_activated_time",
        translation_key="last_activated_time",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda bike: bike.last_activated_time,
    ),
)


class BMWMotorradSensor(BMWMotorradEntity, SensorEntity):
    entity_description: BMWMotorradSensorDescription

    def __init__(self, coordinator, bike_id: str, description: BMWMotorradSensorDescription) -> None:
        super().__init__(coordinator, bike_id)
        self.entity_description = description
        self._attr_unique_id = f"{bike_id}_{description.key}"

    @property
    def native_value(self):
        return self.entity_description.value_fn(self.bike)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = entry.runtime_data.coordinator
    entities: list[SensorEntity] = []
    for bike_id in coordinator.data:
        for description in SENSORS:
            entities.append(BMWMotorradSensor(coordinator, bike_id, description))
    async_add_entities(entities)
