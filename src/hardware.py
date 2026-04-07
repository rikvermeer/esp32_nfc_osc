import machine
import time
import binascii
from pn532.i2c import PN532_I2C
from ssd1306 import SSD1306_I2C

DEBUG = False

TCA9548A_ADDRESS = 0x70
PN532_I2C_ADDR = 0x24
SSD1306_I2C_ADDR = 0x3C
SSD1306_I2C_ADDR2 = 0x3D

WIDTH = 128
HEIGHT = 64

i2c = None

def init_i2c():
    """Initialize I2C bus"""
    global i2c
    i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
    print(i2c.scan())
    return i2c

def select_bus(bus):
    """Select specific I2C bus on multiplexer"""
    if bus > 7:
        return
    i2c.writeto(TCA9548A_ADDRESS, bytearray([1 << bus]))

def scan_hardware():
    """Scan all buses and detect NFC readers and LCD displays"""
    if i2c is None:
        init_i2c()
    
    nfc_readers = {}
    lcd_displays = {}
    
    for nfc_bus in range(8):
        select_bus(nfc_bus)
        time.sleep(0.1)
        devices = i2c.scan()
        print(f"Bus {nfc_bus}: {len(devices)} devices found")
        
        for device in devices:
            if device == PN532_I2C_ADDR:
                nfc_readers[nfc_bus] = PN532_I2C(i2c, PN532_I2C_ADDR, debug=DEBUG)
                print(f"NFC reader found on bus {nfc_bus}")
            elif device == SSD1306_I2C_ADDR:
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
            time.sleep(0.1)
    
    print(f"Found {len(nfc_readers)} NFC devices and {len(lcd_displays)} displays")
    print(nfc_readers)
    print(lcd_displays)
    
    return nfc_readers, lcd_displays

def create_nfc_lcd_mapping(nfc_readers, lcd_displays):
    """Map NFC readers to LCD displays"""
    nfc_lcd_mapping = {}
    
    if len(nfc_readers) and len(lcd_displays):
        lcd_index = 0
        nfc_keys = sorted(nfc_readers.keys())
        lcd_keys = sorted(lcd_displays.keys())
        
        for nfc_bus in nfc_keys:
            lcd_bus = lcd_keys[lcd_index]
            nfc_lcd_mapping[nfc_bus] = lcd_bus
            lcd_index += 1
            if lcd_index >= len(lcd_keys):
                break
    
    print("NFC-LCD Mapping:")
    print(nfc_lcd_mapping)
    return nfc_lcd_mapping

def read_nfc_tag(nfc_reader):
    """Read NFC tag and return UID as hex string"""
    try:
        uid = nfc_reader.read_passive_target(timeout=50)
        if uid:
            hex_uid = binascii.hexlify(uid).decode('utf-8')
            print(f"UID (read_nfc_tag): {hex_uid}")
            return hex_uid
        else:
            return None
    except Exception as e:
        print(f"Error reading NFC tags: {e}")
        return None

def print_lcd(display, text):
    """Print text on LCD display"""
    display.fill(0)
    lines = text.split('\n')
    for i, line in enumerate(lines):
        display.text(line, 0, i * 10)
    display.show()

def get_track_ids_for_nfc_reader(nfc_reader, nfc_readers):
    """Get track IDs for specific NFC reader (6 tracks per reader)"""
    nfc_index = 0
    for nfc_bus in sorted(nfc_readers.keys()):
        if nfc_readers[nfc_bus] == nfc_reader:
            print(f"NFC reader found on bus {nfc_bus}")
            print(f"NFC index: {nfc_index}")
            track_ids = [
                nfc_index * 6,
                nfc_index * 6 + 1,
                nfc_index * 6 + 2,
                nfc_index * 6 + 3,
                nfc_index * 6 + 4,
                nfc_index * 6 + 5
            ]
            print(f"Track ids for reader {nfc_index}: {track_ids}")
            return track_ids
        nfc_index += 1
    return []
