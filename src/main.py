import machine
import time
#from ubinascii import hexlify
from pn532.i2c import PN532_I2C
from ssd1306 import SSD1306_I2C
import json
import network
import uosc.client
import binascii

# Debug mode for NFC readers; clutters the output if True
DEBUG = False

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

# Load mapping from JSON file
with open('/mapping.json', 'r') as f:
    mapping = json.load(f)

# Initialize I2C
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
print(i2c.scan())

# WiFi Configuration
WIFI_SSID = 'network'
WIFI_PASSWORD = 'password'

# OSC Configuration (send to local OSC router on your computer)
OSC_SERVER_IP = '192.168.1.3'  # IP of computer running ableton (OSC)
OSC_SERVER_PORT = 11000
# Create OSC client
client = uosc.client.Client(OSC_SERVER_IP, OSC_SERVER_PORT)
wlan = network.WLAN(network.STA_IF)

# Connect to WiFi
def connect_wifi():
    """Connect to WiFi network"""
    # wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            pass
    print('Network config:', wlan.ifconfig())

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
            # Convert UID to hex string for consistent output
            hex_uid = binascii.hexlify(uid).decode('utf-8')
            print(f"UID (read_nfc_tag): {hex_uid}")
            return hex_uid
        else:
            #print("No Tag detected")
            return None
    except Exception as e:
        print(f"Error reading NFC tags: {e}")
        return None

# Function to print text on the LCD
def print_lcd(display, text):
    # display.fill(0)
    # display.text(text, 0, 0)
    # display.show()
    display.fill(0)  # Clear the display
    # Split text by lines
    lines = text.split('\n')
    for i, line in enumerate(lines):
        # Adjust the position for each line if necessary
        display.text(line, 0, i * 10)  # Assuming 10 pixels per line height
    display.show()

def get_display_bus_for_nfc_bus(nfc_bus):
    try:
        lcd_bus = nfc_lcd_mapping[nfc_bus]
        return lcd_bus
    except KeyError:
        print(f"No display found for NFC reader on bus {nfc_bus}")
        return None

# Get track ids for nfc reader. 
#   Reader 0 controls tracks 0-5, 
#   Reader 1 controls tracks 6-11,
#   Reader 2 controls tracks 12-17,
#   Reader 3 controls tracks 18-23,
def get_track_ids_for_nfc_reader(nfc_reader):
    # Use the mapping to find the index for the given NFC reader
    nfc_index = 0
    for nfc_bus in sorted(nfc_readers.keys()):
        if nfc_readers[nfc_bus] == nfc_reader:
            print(f"NFC reader found on bus {nfc_bus}")
            print(f"NFC index: {nfc_index}")
            track_ids = [nfc_index * 6, nfc_index * 6 + 1, nfc_index * 6 + 2, nfc_index * 6 + 3, nfc_index * 6 + 4, nfc_index * 6 + 5]
            print(f"Track ids for reader {nfc_index}: {track_ids}")
            return track_ids
        nfc_index += 1
    # If the reader is not found, return an empty list or handle the error
    return []

def get_display(bus):
    try:
        return lcd_displays[bus]
    except KeyError:
        print(f"No display found for bus {bus}")
        return None

def osc_fire_clip(track_id, clip_id=0):
    """Send OSC message to Ableton"""
    try:     
        # Send OSC message with UID and clip index
        client.send('/live/clip/fire', track_id, clip_id)
        print(f"Sent OSC: /live/clip/fire {track_id} {clip_id}")
    except Exception as e:
        print(f"Error sending OSC message: {e}")

def osc_stop_track_all_clips(track_id):
    """Send OSC clear event when a tag is removed"""
    try:
        client.send('/live/track/stop_all_clips', track_id)
        #print(f"Sent OSC: /live/track/stop_all_clips")
    except Exception as e:
        pass
        #print(f"Error sending OSC clear: {e}")

def osc_stop_tracks(track_ids):
    for track_id in track_ids:
        osc_stop_track_all_clips(track_id)

# Scan all buses on the multiplexer
for nfc_bus in range(8):
    select_bus(nfc_bus)
    time.sleep(0.1)  # Allow time for bus switch
    devices = i2c.scan()
    print(f"Bus {nfc_bus}: {len(devices)} devices found")

    for device in devices:
        if device == PN532_I2C_ADDR:
            nfc_readers[nfc_bus] = PN532_I2C(i2c, PN532_I2C_ADDR, debug=DEBUG)
            print(f"NFC reader found on bus {nfc_bus}")
        elif device == SSD1306_I2C_ADDR:
            # Initialize I2C for SSD1306
            display = SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=SSD1306_I2C_ADDR)
            lcd_displays[nfc_bus] = display
            print(f"LCD found on bus {nfc_bus}")
        elif device == SSD1306_I2C_ADDR2:
            display = SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=SSD1306_I2C_ADDR2)
            lcd_displays[nfc_bus] = display
            print(f"LCD found on bus {nfc_bus}")
        elif device == TCA9548A_ADDRESS:
            print(f"Multiplexer (master) found on bus {nfc_bus}")
        else:
            print(f"Unknown device found on bus {nfc_bus}")
        time.sleep(.1)

print(f"Found the following NFC {len(nfc_readers)} devices and {len(lcd_displays)} displays:")
print(nfc_readers)
print(lcd_displays)


# Map NFC readers to LCD displays
if len(nfc_readers) and len(lcd_displays):
    lcd_index = 0
    # Sort the keys of nfc_readers
    nfc_keys = sorted(nfc_readers.keys())
    # Sort the keys of lcd_displays
    lcd_keys = sorted(lcd_displays.keys())
    for nfc_bus in nfc_keys:
        lcd_bus = lcd_keys[lcd_index]
        nfc_lcd_mapping[nfc_bus] = lcd_bus
        lcd_index += 1
        if lcd_index >= len(lcd_keys):
            break

print("Mapping:")
print(nfc_lcd_mapping)
print("\n")

print(mapping)
print(f"DEMO Tag id for 33c29c92: {mapping.get("33c29c92")}")
print("\n")

def main():
    connect_wifi()
    try:
        # Main loop
        while True:
            # Iterate over each NFC reader
            for nfc_bus, nfc_reader in nfc_readers.items():
                select_bus(nfc_bus)
                print(f"Bus {nfc_bus}: {nfc_reader} selected")
                # Read NFC tag
                uid = read_nfc_tag(nfc_reader)
                track_ids = get_track_ids_for_nfc_reader(nfc_reader)
                tag_id = None
                track_id = None
                print(f"Track ids: {track_ids}")
                if uid:
                    tag_id = mapping.get(uid, None)
                    if tag_id is None:
                        print(f"Tag id not found for uid: {uid}")
                        continue
                    print(f"Tag id: {tag_id}")
                    osc_stop_tracks(track_ids)
                    track_id = track_ids[tag_id]
                    osc_fire_clip(track_id)
                else:
                    osc_stop_tracks(track_ids)
                
                # Get display bus for this NFC reader
                display_bus = get_display_bus_for_nfc_bus(nfc_bus)
                display = get_display(display_bus)
                # print(f"Display bus: {display_bus}")
                # print(f"Display: {display}")
                # Display the UID on the connected LCD
                if display:
                    select_bus(display_bus)
                    min_track_id = min(track_ids)
                    max_track_id = max(track_ids)
                    track_ids_str = f"{min_track_id}/{max_track_id}"
                    if uid:
                        lcd_text = f"NFC id:{uid} \nTag id: {tag_id}\nTrack id: {track_id}"
                        print_lcd(display, lcd_text)
                    else:
                        lcd_text = f"No Tag detected\nStopping tracks:\n{track_ids_str}"
                        if not wlan.isconnected():
                            lcd_text = f"No WiFi\n" + lcd_text
                        print_lcd(display, lcd_text)
                else:
                    print(f"No display found for NFC reader on bus {nfc_bus}")
            # Sleep for a short period to avoid busy waiting
            time.sleep(.1)
    except Exception as e:
        print(f"Error in main loop: {e}")
        client.close()

if __name__ == "__main__":
    main()