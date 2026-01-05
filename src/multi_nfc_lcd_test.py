import machine
import time
from ubinascii import hexlify
from pn532.i2c import PN532_I2C
from ssd1306 import SSD1306_I2C

# Define the I2C multiplexer address
TCA9548A_ADDRESS = 0x70
# NFC Reader address
PN532_I2C_ADDR = 0x24
# LCD address
SSD1306_I2C_ADDR = 0x3C
SSD1306_I2C_ADDR2 = 0x3D

# LCD dimensions
WIDTH = 128
HEIGHT = 64

nfc_readers = {}
lcd_displays = {}
#Which lcd displays info for which nfc reader
nfc_lcd_mapping = {}

# Initialize I2C
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
print(i2c.scan())

# Function to select a specific I2C bus on the multiplexer
def select_bus(bus):
    if bus > 7:
        return
    i2c.writeto(TCA9548A_ADDRESS, bytearray([1 << bus]))

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

# Function to print text on the LCD
def print_lcd(display, text):
    display.fill(0)
    display.text(text, 0, 0)
    display.show()

def get_display_bus_for_nfc_bus(nfc_bus):
    try:
        lcd_bus = nfc_lcd_mapping[nfc_bus]
        return lcd_bus
    except KeyError:
        print(f"No display found for NFC reader on bus {nfc_bus}")
        return None

def get_display(bus):
    try:
        return lcd_displays[bus]
    except KeyError:
        print(f"No display found for bus {bus}")
        return None

# Scan all buses on the multiplexer
for nfc_bus in range(8):
    select_bus(nfc_bus)
    time.sleep(0.1)  # Allow time for bus switch
    devices = i2c.scan()
    print(f"Bus {nfc_bus}: {len(devices)} devices found")

    for device in devices:
        print(f" - Device at address: {hex(device)}")
        if device == PN532_I2C_ADDR:
            nfc_readers[nfc_bus] = PN532_I2C(i2c, PN532_I2C_ADDR, debug=True)
        elif device == SSD1306_I2C_ADDR:
            # Initialize I2C for SSD1306
            display = SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=SSD1306_I2C_ADDR)
            lcd_displays[nfc_bus] = display
        elif device == SSD1306_I2C_ADDR2:
            display = SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=SSD1306_I2C_ADDR2)
            lcd_displays[nfc_bus] = display
        time.sleep(.1)

# Map NFC readers to LCD displays
if len(nfc_readers) and len(lcd_displays):
    lcd_index = 0
    for nfc_bus in nfc_readers.keys():
        lcd_bus = list(lcd_displays.keys())[lcd_index]
        nfc_lcd_mapping[nfc_bus] = lcd_bus
        lcd_index += 1
        if lcd_index >= len(lcd_displays):
            break

# Main loop
while True:
    # Iterate over each NFC reader
    for nfc_bus, nfc_reader in nfc_readers.items():
        select_bus(nfc_bus)
        print(f"Bus {nfc_bus}: {nfc_reader} selected")
        # Read NFC tag
        uid = read_nfc_tag(nfc_reader)
        # Get display bus for this NFC reader
        display_bus = get_display_bus_for_nfc_bus(nfc_bus)
        display = get_display(display_bus)
        # Display the UID on the connected LCD
        if display_bus and display:
            select_bus(display_bus)
            print_lcd(display, uid if uid else "No Tag detected")
            print(f"UID: {uid}")
        else:
            print(f"No display found for NFC reader on bus {nfc_bus}")
    # Sleep for a short period to avoid busy waiting
    time.sleep(.1)