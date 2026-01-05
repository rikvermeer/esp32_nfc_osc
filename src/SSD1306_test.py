import machine
import time
from ssd1306 import SSD1306_I2C

# Define the I2C multiplexer address
TCA9548A_ADDRESS = 0x70
# LCD address
SSD1306_I2C_ADDR = 0x3C
SSD1306_I2C_ADDR2 = 0x3D

# Initialize I2C
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
print(i2c.scan())

# Function to select a specific I2C bus on the multiplexer
def select_bus(bus):
    if bus > 7:
        return
    i2c.writeto(TCA9548A_ADDRESS, bytearray([1 << bus]))

WIDTH = 128
HEIGHT = 64
lcd_displays = {}
def print_lcd(display, text):
    display.fill(0)
    display.text(text, 0, 0)
    display.show()
    
# Scan all buses
for bus in range(8):
    select_bus(bus)
    time.sleep(0.1)  # Allow time for bus switch
    devices = i2c.scan()
    print(f"Bus {bus}: {len(devices)} devices found")
    for device in devices:
        print(f" - Device at address: {hex(device)}")
        if device == SSD1306_I2C_ADDR:
            # Initialize I2C for SSD1306
            display = SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=SSD1306_I2C_ADDR)
            lcd_displays[bus] = display
            time.sleep(.5)
        elif device == SSD1306_I2C_ADDR2:
            display = SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=SSD1306_I2C_ADDR2)
            lcd_displays[bus] = display
            time.sleep(.5)


for bus, lcd_display in lcd_displays.items():
    print(f"Bus {bus}: {lcd_display}")
    lcd_display = lcd_displays[bus]
    select_bus(bus)
    print_lcd(lcd_display, str(bus))
    time.sleep(.5)