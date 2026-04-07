from machine import Pin, SPI
import time
from pn532.spi import PN532_SPI

MOSI = 23
CLK = 18
MISO = 19
CS1 = 32
CS2 = 22

print("=== PN532 Dual Reader Test ===")
print(f"Pin Configuration:")
print(f"  MOSI:   GPIO{MOSI}")
print(f"  CLK:    GPIO{CLK}")
print(f"  MISO:   GPIO{MISO}")
print(f"  CS1:    GPIO{CS1}")
print(f"  CS2:    GPIO{CS2}")
print(f"  RESET:  Not connected")
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

print("\nInitializing CS pins...")
cs1 = Pin(CS1, Pin.OUT)
cs1.value(1)
cs2 = Pin(CS2, Pin.OUT)
cs2.value(1)
print("CS pins configured - both deselected")
time.sleep(0.5)

print("\n--- Initializing Reader 1 (CS=GPIO{}) ---".format(CS1))
try:
    nfc1 = PN532_SPI(spi, cs_pin=cs1, reset=None, debug=True)
    print(f"Reader 1 OK - Firmware: {nfc1.firmware_version}")
    nfc1.SAM_configuration()
    print("Reader 1 SAM configured")
    time.sleep(0.2)
except Exception as e:
    print(f"Reader 1 FAILED: {e}")
    import sys
    sys.print_exception(e)
    nfc1 = None

print("\n--- Initializing Reader 2 (CS=GPIO{}) ---".format(CS2))
try:
    nfc2 = PN532_SPI(spi, cs_pin=cs2, reset=None, debug=False)
    print(f"Reader 2 OK - Firmware: {nfc2.firmware_version}")
    nfc2.SAM_configuration()
    print("Reader 2 SAM configured")
    time.sleep(0.2)
except Exception as e:
    print(f"Reader 2 FAILED: {e}")
    import sys
    sys.print_exception(e)
    nfc2 = None

if not nfc1 and not nfc2:
    print("\nNo readers initialized successfully. Exiting.")
else:
    print("\n=== Ready to read cards ===")
    print("Reader 1: CS=GPIO{}".format(CS1))
    print("Reader 2: CS=GPIO{}".format(CS2))
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            if nfc1:
                uid1 = nfc1.read_passive_target(timeout=100)
                if uid1:
                    print("[Reader 1] Card detected!")
                    print("  UID: {}".format(' '.join(['%02X' % b for b in uid1])))
                    print("  Length: {} bytes".format(len(uid1)))
                    print()
            
            if nfc2:
                uid2 = nfc2.read_passive_target(timeout=100)
                if uid2:
                    print("[Reader 2] Card detected!")
                    print("  UID: {}".format(' '.join(['%02X' % b for b in uid2])))
                    print("  Length: {} bytes".format(len(uid2)))
                    print()
            
            time.sleep(0.1)
                
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
