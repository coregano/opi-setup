from bluepy import btle
from bluepy.btle import UUID, Peripheral

# UUIDs of the FSR service and characteristic
fsr_service_uuid = UUID(0xA000)
fsr_characteristic_uuid = UUID(0xA001)

# MAC address of the Adafruit nRF52840 device
device_mac = "C8:8F:38:D2:B5:5A"  # Replace with your device's MAC address

# Connect to the device
device = Peripheral(device_mac)

# Find the FSR service
fsr_service = device.getServiceByUUID(fsr_service_uuid)

# Find the FSR characteristic
fsr_characteristic = fsr_service.getCharacteristics(fsr_characteristic_uuid)[0]

# Enable notifications for the FSR characteristic
cccd_uuid = "00002902-0000-1000-8000-00805f9b34fb"  # CCCD UUID
cccd_handle = fsr_characteristic.getHandle() + 1  # Handle of the CCCD descriptor

# Write the value 0x0001 to enable notifications
device.writeCharacteristic(cccd_handle, b"\x01\x00", withResponse=True)

# Close the connection
device.disconnect()
