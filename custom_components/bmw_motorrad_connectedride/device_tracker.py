from __future__ import annotations

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker.const import SourceType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import BMWMotorradEntity


class BMWMotorradTracker(BMWMotorradEntity, TrackerEntity):
    _attr_name = "Location"
    _attr_icon = "mdi:map-marker"

    def __init__(self, coordinator, bike_id: str) -> None:
        super().__init__(coordinator, bike_id)
        self._attr_unique_id = f"{bike_id}_tracker"

    @property
    def latitude(self):
        return self.bike.latitude

    @property
    def longitude(self):
        return self.bike.longitude

    @property
    def source_type(self):
        return SourceType.GPS if self.bike.latitude is not None and self.bike.longitude is not None else None


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data.coordinator
    async_add_entities([BMWMotorradTracker(coordinator, bike_id) for bike_id in coordinator.data])
