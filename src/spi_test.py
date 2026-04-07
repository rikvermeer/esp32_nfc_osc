from machine import Pin, SPI
import time

MOSI = 23
CLK = 18
MISO = 19
CS = 32

print("Starting SPI test...")
print(f"MOSI: GPIO{MOSI}")
print(f"CLK:  GPIO{CLK}")
print(f"MISO: GPIO{MISO}")
print(f"CS:   GPIO{CS}")

cs = Pin(CS, Pin.OUT)
cs.value(1)

spi = SPI(
    1,
    baudrate=1000000,
    polarity=0,
    phase=0,
    sck=Pin(CLK),
    mosi=Pin(MOSI),
    miso=Pin(MISO)
)

print("\nSPI initialized - 1MHz, Mode 0 (CPOL=0, CPHA=0)")
print("\nStarting test pattern transmission...")
print("Press Ctrl+C to stop\n")

test_patterns = [
    b'\x00',
    b'\xFF',
    b'\xAA',
    b'\x55',
    b'\x01\x02\x03\x04\x05',
    b'\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99\xAA\xBB\xCC\xDD\xEE\xFF',
]

pattern_names = [
    "All zeros (0x00)",
    "All ones (0xFF)",
    "Alternating bits (0xAA)",
    "Alternating bits (0x55)",
    "Incrementing bytes",
    "Full byte range",
]

try:
    while True:
        for i, (pattern, name) in enumerate(zip(test_patterns, pattern_names)):
            print(f"Pattern {i+1}: {name}")
            data_hex = ' '.join(['%02X' % b for b in pattern])
            print(f"  Data: {data_hex}")
            
            cs.value(0)
            time.sleep_us(10)
            
            rxdata = bytearray(len(pattern))
            spi.write_readinto(pattern, rxdata)
            
            time.sleep_us(10)
            cs.value(1)
            
            print(f"  Sent: {len(pattern)} bytes")
            rx_hex = ' '.join(['%02X' % b for b in rxdata])
            print(f"  RX:   {rx_hex}")
            print()
            
            time.sleep(1)
        
        print("--- Cycle complete, repeating... ---\n")
        time.sleep(2)

except KeyboardInterrupt:
    print("\nTest stopped")
    cs.value(1)
    spi.deinit()
    print("SPI deinitialized")
