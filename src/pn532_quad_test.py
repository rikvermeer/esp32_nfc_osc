from machine import Pin, SPI
import time
from pn532.spi import PN532_SPI

MOSI = 23
CLK = 18
MISO = 19
CS1 = 32
CS2 = 22
CS3 = 13
CS4 = 4

print("=== PN532 Quad Reader Test ===")
print(f"Pin Configuration:")
print(f"  MOSI:   GPIO{MOSI}")
print(f"  CLK:    GPIO{CLK}")
print(f"  MISO:   GPIO{MISO}")
print(f"  CS1:    GPIO{CS1}")
print(f"  CS2:    GPIO{CS2}")
print(f"  CS3:    GPIO{CS3}")
print(f"  CS4:    GPIO{CS4}")
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
cs_pins = [
    Pin(CS1, Pin.OUT),
    Pin(CS2, Pin.OUT),
    Pin(CS3, Pin.OUT),
    Pin(CS4, Pin.OUT)
]
for cs in cs_pins:
    cs.value(1)
print("All CS pins configured - deselected")
time.sleep(0.5)

readers = []
cs_numbers = [CS1, CS2, CS3, CS4]

for i, (cs_pin, cs_num) in enumerate(zip(cs_pins, cs_numbers), 1):
    print(f"\n--- Initializing Reader {i} (CS=GPIO{cs_num}) ---")
    try:
        nfc = PN532_SPI(spi, cs_pin=cs_pin, reset=None, debug=False)
        print(f"Reader {i} OK - Firmware: {nfc.firmware_version}")
        nfc.SAM_configuration()
        print(f"Reader {i} SAM configured")
        readers.append((i, nfc, cs_num))
        time.sleep(0.2)
    except Exception as e:
        print(f"Reader {i} FAILED: {e}")
        readers.append((i, None, cs_num))

active_readers = [r for r in readers if r[1] is not None]

if not active_readers:
    print("\nNo readers initialized successfully. Exiting.")
else:
    print(f"\n=== {len(active_readers)} Reader(s) Active ===")
    for num, _, cs_num in active_readers:
        print(f"Reader {num}: CS=GPIO{cs_num}")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            for num, nfc, cs_num in active_readers:
                uid = nfc.read_passive_target(timeout=100)
                if uid:
                    print(f"[Reader {num} - GPIO{cs_num}] Card detected!")
                    print("  UID: {}".format(' '.join(['%02X' % b for b in uid])))
                    print("  Length: {} bytes".format(len(uid)))
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
