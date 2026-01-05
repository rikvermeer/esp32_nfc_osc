import machine
import time
from ubinascii import hexlify
from pn532.i2c import PN532_I2C

# Define the I2C multiplexer address
TCA9548A_ADDRESS = 0x70
# NFC Reader address
PN532_I2C_ADDR = 0x24

# Initialize I2C
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
print(i2c.scan())

# Function to select a specific I2C bus on the multiplexer
def select_bus(bus):
    if bus > 7:
        return
    i2c.writeto(TCA9548A_ADDRESS, bytearray([1 << bus]))

nfc_readers = {}
# Read and handle UIDs
def read_nfc_tag(nfc_reader):
    try:
        uid = nfc_reader.read_passive_target(timeout=50)
        if uid:
            uid = hexlify(uid).decode('utf-8')
            print(f"UID: {uid}")
            return uid
        else:
            print("No Tag detected")
            return None
    except Exception as e:
        print(f"Error reading NFC tags: {e}")
        return None



# Scan all buses
for bus in range(8):
    select_bus(bus)
    time.sleep(0.1)  # Allow time for bus switch
    devices = i2c.scan()
    print(f"Bus {bus}: {len(devices)} devices found")
    for device in devices:
        print(f" - Device at address: {hex(device)}")
        if device == PN532_I2C_ADDR:
            nfc_readers[bus] = PN532_I2C(i2c, PN532_I2C_ADDR, debug=True)
            time.sleep(.2)

while True:
    for bus, reader in nfc_readers.items():
        print(f"Bus {bus}: {reader}")
        nfc_reader = nfc_readers[bus]
        select_bus(bus)
        uid = read_nfc_tag(nfc_reader)
        if uid:
            uid = hexlify(uid).decode('utf-8')
            print(f"UID: {uid}")
        time.sleep(.5)
    time.sleep(.1)