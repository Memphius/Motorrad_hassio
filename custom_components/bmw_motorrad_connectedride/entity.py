from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_RAW, DOMAIN
from .coordinator import BMWMotorradCoordinator
from .models import BikeData


class BMWMotorradEntity(CoordinatorEntity[BMWMotorradCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: BMWMotorradCoordinator, bike_id: str) -> None:
        super().__init__(coordinator)
        self.bike_id = bike_id

    @property
    def bike(self) -> BikeData:
        return self.coordinator.data[self.bike_id]

    @property
    def device_info(self) -> DeviceInfo:
        bike = self.bike
        return DeviceInfo(
            identifiers={(DOMAIN, self.bike_id)},
            manufacturer="BMW Motorrad",
            model=bike.type_key or "ConnectedRide bike",
            name=bike.type_key or f"BMW Motorrad {self.bike_id}",
            serial_number=self.bike_id,
        )

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        return {ATTR_RAW: self.bike.raw}
