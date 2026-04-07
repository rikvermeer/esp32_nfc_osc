"""
ST7789 Display Test
Verify display functionality on shared SPI bus

Pin Configuration:
- MOSI: GPIO 23
- MISO: GPIO 19
- CLK:  GPIO 18
- CS:   GPIO 21
- DC:   GPIO 17
- RST:  GPIO 16
- BL:   3.3V (always on)
"""

import time
from machine import Pin, SPI
from lib.st7735s import ST7735S, BLACK, BLUE, RED, GREEN, CYAN, MAGENTA, YELLOW, WHITE

def main():
    print("Initializing ST7735S display...")
    
    # Initialize SPI bus
    spi = SPI(
        1,
        baudrate=60000000,  # 10 MHz (more conservative for ST7735S)
        polarity=0,
        phase=0,
        sck=Pin(18),
        mosi=Pin(23),
        miso=Pin(19)
    )
    
    # Initialize display
    display = ST7735S(
        spi,
        cs=Pin(21, Pin.OUT),
        dc=Pin(17, Pin.OUT),
        rst=Pin(16, Pin.OUT),
        width=240,#128,
        height=240,#160,
        rotation=0,  # 0=portrait, 1=landscape, 2=inverted portrait, 3=inverted landscape
        xstart=2,  # Column offset to fix border
        ystart=1   # Row offset to fix border
    )
    
    print("Display initialized!")
    
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
    
    display.rect(10, 10, 108, 60, RED)
    display.rect(15, 15, 98, 50, GREEN)
    display.rect(20, 20, 88, 40, BLUE)
    time.sleep(2)
    
    # Test 3: Fill rectangles
    print("Test 3: Filled rectangles...")
    display.fill(BLACK)
    time.sleep(0.2)
    
    display.fill_rect(10, 10, 40, 40, RED)
    display.fill_rect(50, 10, 40, 40, GREEN)
    display.fill_rect(90, 10, 38, 40, BLUE)
    
    display.fill_rect(10, 60, 40, 40, YELLOW)
    display.fill_rect(50, 60, 40, 40, CYAN)
    display.fill_rect(90, 60, 38, 40, MAGENTA)
    time.sleep(2)
    
    # Test 4: Lines
    print("Test 4: Drawing lines...")
    display.fill(BLACK)
    time.sleep(0.2)
    
    # Horizontal lines
    for i in range(0, 160, 10):
        display.hline(0, i, 128, RED)
    time.sleep(1)
    
    # Vertical lines
    display.fill(BLACK)
    for i in range(0, 128, 10):
        display.vline(i, 0, 160, GREEN)
    time.sleep(1)
    
    # Diagonal pattern
    display.fill(BLACK)
    for i in range(0, 128, 4):
        display.line(0, 0, i, 159, BLUE)
        display.line(0, 0, 127, i, CYAN)
    time.sleep(2)
    
    # Test 5: Success message
    print("Test 5: Final display...")
    display.fill(BLACK)
    time.sleep(0.2)
    
    # Draw a border
    display.rect(0, 0, 128, 160, WHITE)
    display.rect(2, 2, 124, 156, GREEN)
    
    # Center success indicator (simple colored blocks)
    display.fill_rect(44, 60, 40, 40, GREEN)
    
    print("\n" + "="*40)
    print("Display test complete!")
    print("If you see colored patterns, it works!")
    print("="*40)
    
    # Keep display on
    while True:
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import sys
        sys.print_exception(e)
