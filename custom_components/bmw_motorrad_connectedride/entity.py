from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_BIKE_ID, ATTR_RAW, DOMAIN


class BMWMotorradEntity(CoordinatorEntity):
    """Base entity for BMW Motorrad ConnectedRide."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, bike_id: str) -> None:
        super().__init__(coordinator)
        self._bike_id = bike_id

    @property
    def bike(self):
        """Return the current bike data for this entity."""
        return self.coordinator.data[self._bike_id]

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        bike = self.bike

        identifiers = {(DOMAIN, self._bike_id)}
        bike_name = bike.name or "BMW Motorrad"

        model_parts: list[str] = []
        if bike.name:
            model_parts.append(bike.name)
        if bike.type_key:
            model_parts.append(f"Type {bike.type_key}")
        model = " - ".join(model_parts) if model_parts else "ConnectedRide bike"

        sw_version = None
        if bike.raw.get("_version") is not None:
            sw_version = str(bike.raw.get("_version"))

        serial_number = bike.vin or self._bike_id

        return DeviceInfo(
            identifiers=identifiers,
            manufacturer="BMW Motorrad",
            name=bike_name,
            model=model,
            serial_number=serial_number,
            sw_version=sw_version,
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._bike_id in self.coordinator.data and self.coordinator.last_update_success

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra attributes."""
        bike = self.bike
        attrs = {
            ATTR_BIKE_ID: self._bike_id,
        }

        if bike.vin:
            attrs["vin"] = bike.vin
        if bike.type_key:
            attrs["type_key"] = bike.type_key
        if bike.color:
            attrs["color"] = bike.color

        attrs[ATTR_RAW] = bike.raw
        return attrs
