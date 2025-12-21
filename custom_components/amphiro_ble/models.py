from __future__ import annotations

import logging
from homeassistant.const import UnitOfTemperature, UnitOfTime

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import DeviceClass, Units

from .const import COMPANY_IDENTIFIER

_LOGGER = logging.getLogger(__name__)


def _convert_advertisement(
    raw_data: bytes,
) -> tuple[str | None, dict[tuple[DeviceClass, Units], float]] | None:
    """
    Convert a Amphiro advertisement to a dictionary of sensor values.
    """
    if raw_data[-3:] == b"\x00\x00\x00":  # Last 3 bytes Seems to be static "0x410000"
        val = raw_data.hex()

        # https://gitlab.com/baze/amphiro_oras_bluetooth_shower_hub/-/blob/main/read_Ampiro_shower.py#L109
        # Construct v1 containing spaced out representation of the raw data
        v1 = ""
        startCounter = int(val[2:6], 16)
        v1 += str(val)[0:8] + " "

        secs = int(val[6:10], 16)
        v1 += str(val)[8:12] + " "

        v1 += str(val)[12:14] + " "

        a = int(val[12:16], 16)
        v1 += str(val)[14:18] + " "

        pulses = int(val[16:22], 16)
        v1 += str(val)[18:24] + " "

        temp = int(val[22:24], 16)
        v1 += str(val)[24:26] + " "

        kwatts = int(val[24:28], 16) / 100
        v1 += str(val)[26:30] + " "

        # Constant 19?
        v1 += str(val)[30:32] + " "

        v1 += str(val)[32:]

        data = {}
        data["session"] = startCounter
        data["second"] = secs
        data["temp"] = temp
        data["kwatts"] = kwatts
        data["pulses"] = pulses
        data["liters"] = round(pulses / 2560, 2)
        data["liters_rounded"] = round(pulses / 2560)
        data["a"] = a
        data = {
            (DeviceClass.COUNT, None): startCounter,
            (DeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS): temp,
            (DeviceClass.ENERGY, Units.ENERGY_KILO_WATT_HOUR): kwatts,
            (DeviceClass.TIME, UnitOfTime.SECONDS): secs,
            (DeviceClass.VOLUME_DISPENSED, Units.VOLUME_LITERS): round(
                pulses / 2560, 2
            ),
        }
        _LOGGER.debug(v1)
        return data
    _LOGGER.error("Amphiro data format not supported: %s", raw_data)

    return None


class AmphiroBluetoothDeviceData(BluetoothData):
    """Data for Amphiro BLE sensors."""

    def _start_update(self, service_info: BluetoothServiceInfo) -> None:
        try:
            raw_data = service_info.manufacturer_data[COMPANY_IDENTIFIER]
        except (KeyError, IndexError):
            _LOGGER.debug("Manufacturer ID not found in data")
            return None

        result = _convert_advertisement(raw_data)
        if result is None:
            return
        self.set_device_type(f"Amphiro {service_info.name}")
        self.set_device_manufacturer("Amphiro")
        identifier = short_address(service_info.address)
        self.set_device_name(f"{service_info.name} {identifier}")
        for (device_class, unit), value in result.items():
            self.update_sensor(
                key=device_class,
                device_class=device_class,
                native_unit_of_measurement=unit,
                native_value=value,
            )
