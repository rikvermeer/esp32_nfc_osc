"""
ST7789 Display Test - Using russhughes st7789_mpy driver
Test display functionality with basic graphics

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

# Pin definitions
MOSI = 23
CLK = 18
MISO = 19
CS = 21
DC = 17
RST = 16

# Display dimensions
WIDTH = 128
HEIGHT = 160
 
print("=== ST7789 Display Test ===")
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
    baudrate=60000000,  # ST7789 can handle up to 62.5MHz
    polarity=0,
    phase=0,
    sck=Pin(CLK),
    mosi=Pin(MOSI),
    miso=Pin(MISO)
)
print("SPI initialized")

# Initialize display
print("Initializing ST7789 display...")
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
display.offset(2,2)


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
    # Test 1: Fill screen with colors
    print("Test 1: Color fills...")
    colors = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE, BLACK]
    color_names = ["RED", "GREEN", "BLUE", "YELLOW", "CYAN", "MAGENTA", "WHITE", "BLACK"]
    
    for color, name in zip(colors, color_names):
        print(f"  - {name}")
        display.fill(color)
        time.sleep(0.5)
    
    # Test 2: Draw rectangles
    print("Test 2: Drawing rectangles...")
    display.fill(BLACK)
    time.sleep(0.2)
    
    display.rect(10, 20, 115, 100, RED)
    display.rect(15, 25, 105, 90, GREEN)
    display.rect(20, 30, 95, 80, BLUE)
    time.sleep(2)
    
    # Test 3: Filled rectangles
    print("Test 3: Filled rectangles...")
    display.fill(BLACK)
    time.sleep(0.2)
    
    display.fill_rect(10, 20, 35, 50, RED)
    display.fill_rect(50, 20, 35, 50, GREEN)
    display.fill_rect(90, 20, 35, 50, BLUE)
    
    display.fill_rect(10, 80, 35, 50, YELLOW)
    display.fill_rect(50, 80, 35, 50, CYAN)
    display.fill_rect(90, 80, 35, 50, MAGENTA)
    time.sleep(2)
    
    # Test 4: Lines
    print("Test 4: Drawing lines...")
    display.fill(BLACK)
    time.sleep(0.2)
    
    # Horizontal lines
    for i in range(20, HEIGHT, 20):
        display.hline(0, i, WIDTH, RED)
    time.sleep(1)
    
    # Vertical lines
    display.fill(BLACK)
    for i in range(10, WIDTH, 20):
        display.vline(i, 0, HEIGHT, GREEN)
    time.sleep(1)
    
    # Diagonal pattern
    display.fill(BLACK)
    for i in range(0, WIDTH, 8):
        display.line(0, 0, i, HEIGHT-1, BLUE)
    for i in range(0, HEIGHT, 8):
        display.line(0, 0, WIDTH-1, i, CYAN)
    time.sleep(2)
    
    # Test 5: 2x2 Grid (like the dashboard)
    print("Test 5: 2x2 Grid dashboard...")
    display.fill(BLACK)
    time.sleep(0.2)
    
    zone_width = WIDTH // 2
    zone_height = HEIGHT // 2
    
    # Draw zones with different colors
    for i in range(4):
        x = (i % 2) * zone_width
        y = (i // 2) * zone_height
        
        # Border color
        border_colors = [WHITE, RED, GREEN, BLUE]
        display.rect(x, y, zone_width, zone_height, border_colors[i])
        
        # Filled indicator in center
        indicator_size = 30
        ix = x + (zone_width - indicator_size) // 2
        iy = y + (zone_height - indicator_size) // 2
        display.fill_rect(ix, iy, indicator_size, indicator_size, border_colors[i])
        
        # Corner marker
        marker_size = 12
        display.fill_rect(x + 2, y + 2, marker_size, marker_size, border_colors[i])
    
    time.sleep(2)
    
    # Test 6: Success screen
    print("Test 6: Final display...")
    display.fill(BLACK)
    time.sleep(0.2)
    
    # Draw border
    display.rect(0, 0, WIDTH, HEIGHT, WHITE)
    display.rect(2, 2, WIDTH-4, HEIGHT-4, GREEN)
    
    # Draw success indicator
    display.fill_rect(WIDTH//2 - 30, HEIGHT//2 - 30, 60, 60, GREEN)
    
    print("\n" + "="*40)
    print("ST7789 Display test complete!")
    print("If you see colored patterns, it works!")
    print("="*40)
    
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
