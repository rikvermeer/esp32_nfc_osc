from machine import Pin, SPI
import time
from pn532.spi import PN532_SPI

MOSI = 23
CLK = 18
MISO = 19
CS = 32
RESET = 27

print("=== PN532 Single Reader Test ===")
print(f"Pin Configuration:")
print(f"  MOSI:  GPIO{MOSI}")
print(f"  CLK:   GPIO{CLK}")
print(f"  MISO:  GPIO{MISO}")
print(f"  CS:    GPIO{CS}")
print(f"  RESET: GPIO{RESET}")
print()

print("Initializing SPI bus...")
spi = SPI(
    1,
    baudrate=1000000,
    polarity=0,
    phase=0,
    sck=Pin(CLK),
    mosi=Pin(MOSI),
    miso=Pin(MISO)
)
print("SPI initialized: 1MHz, Mode 0")

print("\nInitializing CS and RESET pins...")
cs = Pin(CS, Pin.OUT)
cs.value(1)
reset = Pin(RESET, Pin.OUT, value=1)
print("Pins configured")

print("\nInitializing PN532...")
try:
    nfc = PN532_SPI(spi, cs_pin=cs, reset=reset, debug=True)
    print("\nPN532 initialization successful!")
    print(f"Firmware version: {nfc.firmware_version}")
    
    print("\nConfiguring SAM (Secure Access Module)...")
    nfc.SAM_configuration()
    print("SAM configured")
    
    print("\n=== Ready to read cards ===")
    print("Hold a MiFare/NFC card near the reader...")
    print("Press Ctrl+C to stop\n")
    
    while True:
        uid = nfc.read_passive_target(timeout=500)
        if uid:
            print("Card detected!")
            print(f"  UID: {' '.join(['%02X' % b for b in uid])}")
            print(f"  UID Length: {len(uid)} bytes")
            print()
            time.sleep(2)
        else:
            print(".", end="")
            time.sleep(0.5)
            
except KeyboardInterrupt:
    print("\n\nTest stopped by user")
except Exception as e:
    print(f"\nError: {e}")
    import sys
    sys.print_exception(e)
finally:
    print("Cleaning up...")
    spi.deinit()
    print("SPI deinitialized")
