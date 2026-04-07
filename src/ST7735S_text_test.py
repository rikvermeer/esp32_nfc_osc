"""
ST7735S Character Display Test - Using russhughes st7789_mpy driver
Test text and character display functionality

Pin Configuration:
- MOSI: GPIO 23
- CLK:  GPIO 18
- CS:   GPIO 21
- DC:   GPIO 17
- RST:  GPIO 16
"""

import time
from machine import Pin, SPI
import st7789
import vga1_bold_16x32 as font_large
import vga1_16x16 as font_medium
import vga1_8x16 as font_small

# Pin definitions
MOSI = 23
CLK = 18
MISO = 19
CS = 21
DC = 17
RST = 16

# Display dimensions for ST7735S
WIDTH = 128
HEIGHT = 160

print("=== ST7735S Character Display Test ===")
print(f"Pin Configuration:")
print(f"  MOSI: GPIO{MOSI}")
print(f"  CLK:  GPIO{CLK}")
print(f"  CS:   GPIO{CS}")
print(f"  DC:   GPIO{DC}")
print(f"  RST:  GPIO{RST}")
print()

# Initialize SPI
print("Initializing SPI bus...")
spi = SPI(
    1,
    baudrate=10000000,
    polarity=0,
    phase=0,
    sck=Pin(CLK),
    mosi=Pin(MOSI),
    miso=Pin(MISO)
)
print("SPI initialized")

# Initialize display using st7789 driver for ST7735S
print("Initializing ST7735S display with st7789 driver...")
display = st7789.ST7789(
    spi, 
    WIDTH,
    HEIGHT,
    reset=Pin(RST, Pin.OUT),
    cs=Pin(CS, Pin.OUT),
    dc=Pin(DC, Pin.OUT),
    inversion=False,
    rotation=0
)
display.init()
#display.offset(2, 1)  # ST7735S typical offset

print("Display initialized!")
print()

# Color definitions (RGB565)
BLACK = st7789.BLACK
WHITE = st7789.WHITE
RED = st7789.RED
GREEN = st7789.GREEN
BLUE = st7789.BLUE
CYAN = st7789.CYAN
MAGENTA = st7789.MAGENTA
YELLOW = st7789.YELLOW

try:
    # Test 1: Clear screen
    print("Test 1: Clear screen...")
    display.fill(BLACK)
    time.sleep(0.5)
    
    # Test 2: Display large text
    print("Test 2: Large font test...")
    display.fill(BLACK)
    display.text(font_large, "HELLO", 10, 20, WHITE, BLACK)
    display.text(font_large, "WORLD", 10, 60, GREEN, BLACK)
    time.sleep(2)
    
    # Test 3: Medium font with colors
    print("Test 3: Medium font colors...")
    display.fill(BLACK)
    display.text(font_medium, "Red Text", 10, 10, RED, BLACK)
    display.text(font_medium, "Green", 10, 30, GREEN, BLACK)
    display.text(font_medium, "Blue", 10, 50, BLUE, BLACK)
    display.text(font_medium, "Cyan", 10, 70, CYAN, BLACK)
    display.text(font_medium, "Yellow", 10, 90, YELLOW, BLACK)
    display.text(font_medium, "Magenta", 10, 110, MAGENTA, BLACK)
    time.sleep(3)
    
    # Test 4: Small font - display more text
    print("Test 4: Small font test...")
    display.fill(BLACK)
    display.text(font_small, "NFC Reader", 10, 5, WHITE, BLACK)
    display.text(font_small, "Zone 1:EMPTY", 5, 25, CYAN, BLACK)
    display.text(font_small, "Zone 2:EMPTY", 5, 45, CYAN, BLACK)
    display.text(font_small, "Zone 3:EMPTY", 5, 65, CYAN, BLACK)
    display.text(font_small, "Zone 4:EMPTY", 5, 85, CYAN, BLACK)
    display.text(font_small, "WiFi:OK", 10, 110, GREEN, BLACK)
    display.text(font_small, "OSC:Ready", 10, 130, GREEN, BLACK)
    time.sleep(3)
    
    # Test 5: Numbers and symbols
    print("Test 5: Numbers and symbols...")
    display.fill(BLACK)
    display.text(font_medium, "0123456789", 5, 10, WHITE, BLACK)
    display.text(font_medium, "!@#$%^&*()", 5, 30, YELLOW, BLACK)
    display.text(font_medium, "+-=<>?/\\", 5, 50, CYAN, BLACK)
    display.text(font_medium, "[]{};:,.", 5, 70, MAGENTA, BLACK)
    time.sleep(3)
    
    # Test 6: Character scrolling
    print("Test 6: Scrolling text...")
    messages = [
        "Initializing...",
        "Connecting...",
        "WiFi OK",
        "OSC Ready",
        "NFC Active",
        "System Ready"
    ]
    
    for msg in messages:
        display.fill(BLACK)
        display.text(font_medium, msg, 10, 60, GREEN, BLACK)
        time.sleep(0.8)
    
    # Test 7: Dashboard simulation
    print("Test 7: Dashboard layout...")
    display.fill(BLACK)
    
    # Title
    display.text(font_small, "NFC Controller", 10, 2, WHITE, BLACK)
    display.hline(0, 15, WIDTH, WHITE)
    
    # Zone indicators
    zones = ["Z1", "Z2", "Z3", "Z4"]
    colors = [GREEN, CYAN, YELLOW, MAGENTA]
    
    for i, (zone, color) in enumerate(zip(zones, colors)):
        x = 10 if i % 2 == 0 else 70
        y = 25 + (i // 2) * 35
        
        # Zone box
        display.rect(x-2, y-2, 50, 30, color)
        display.text(font_small, zone, x+2, y+2, color, BLACK)
        display.text(font_small, "EMPTY", x+2, y+14, WHITE, BLACK)
    
    # Status bar at bottom
    display.hline(0, 110, WIDTH, WHITE)
    display.text(font_small, "WiFi:OK", 5, 115, GREEN, BLACK)
    display.text(font_small, "OSC:ON", 5, 130, GREEN, BLACK)
    display.text(font_small, "IP:Ready", 5, 145, CYAN, BLACK)
    
    time.sleep(3)
    
    # Test 8: Animated counter
    print("Test 8: Counter animation...")
    for count in range(10):
        display.fill_rect(20, 60, 88, 40, BLACK)
        display.text(font_large, str(count), 50, 70, YELLOW, BLACK)
        time.sleep(0.3)
    
    # Test 9: Final success screen
    print("Test 9: Success screen...")
    display.fill(BLACK)
    display.rect(5, 5, WIDTH-10, HEIGHT-10, GREEN)
    display.text(font_large, "TEST", 25, 50, GREEN, BLACK)
    display.text(font_large, "PASS!", 20, 90, GREEN, BLACK)
    
    print("\n" + "="*45)
    print("ST7735S Character Display test complete!")
    print("All character tests passed successfully!")
    print("="*45)
    
    # Keep display on
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nTest interrupted by user")
    display.fill(BLACK)
except Exception as e:
    print(f"\nError: {e}")
    import sys
    sys.print_exception(e)
    # Show error on display
    display.fill(RED)
    display.text(font_small, "ERROR!", 30, 70, WHITE, RED)
