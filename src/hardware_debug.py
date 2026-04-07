"""
Comprehensive Hardware Debug Script
Tests each component step-by-step to isolate issues
"""

import time
import machine
from micropython import const

# Pin definitions
SPI_MOSI = 23
SPI_MISO = 19
SPI_CLK = 18

NFC_CS_PINS = [13, 16, 32, 22]
DISPLAY_CS = 21
DISPLAY_DC = 4
DISPLAY_RST = 17
DIP_PINS = [26, 25, 33]

def test_1_gpio_pins():
    """Test 1: Verify all GPIO pins can be initialized"""
    print("\n" + "="*50)
    print("TEST 1: GPIO Pin Initialization")
    print("="*50)
    
    all_pins = [SPI_MOSI, SPI_MISO, SPI_CLK] + NFC_CS_PINS + [DISPLAY_CS, DISPLAY_DC, DISPLAY_RST] + DIP_PINS
    
    for pin_num in all_pins:
        try:
            pin = machine.Pin(pin_num, machine.Pin.OUT)
            pin.value(1)
            time.sleep_ms(10)
            pin.value(0)
            print(f"  ✓ GPIO {pin_num}: OK")
        except Exception as e:
            print(f"  ✗ GPIO {pin_num}: FAILED - {e}")
    
    print("\nGPIO test complete")

def test_2_spi_bus():
    """Test 2: Initialize SPI bus and verify it responds"""
    print("\n" + "="*50)
    print("TEST 2: SPI Bus Initialization")
    print("="*50)
    
    try:
        spi = machine.SPI(
            1,
            baudrate=1000000,
            polarity=0,
            phase=0,
            sck=machine.Pin(SPI_CLK),
            mosi=machine.Pin(SPI_MOSI),
            miso=machine.Pin(SPI_MISO)
        )
        print(f"  ✓ SPI bus initialized")
        print(f"    Baudrate: 1 MHz")
        print(f"    SCK: GPIO {SPI_CLK}")
        print(f"    MOSI: GPIO {SPI_MOSI}")
        print(f"    MISO: GPIO {SPI_MISO}")
        
        # Test SPI write
        test_data = bytearray([0x00, 0xFF, 0xAA, 0x55])
        spi.write(test_data)
        print(f"  ✓ SPI write test: OK")
        
        # Test SPI read
        read_data = bytearray(4)
        spi.readinto(read_data)
        print(f"  ✓ SPI read test: OK (read {len(read_data)} bytes)")
        print(f"    MISO data: {read_data.hex()} (device responses, not loopback)")
        
        return spi
    except Exception as e:
        print(f"  ✗ SPI bus initialization FAILED: {e}")
        return None

def test_3_display_pins():
    """Test 3: Test display control pins"""
    print("\n" + "="*50)
    print("TEST 3: Display Pin Control")
    print("="*50)
    
    try:
        cs = machine.Pin(DISPLAY_CS, machine.Pin.OUT)
        dc = machine.Pin(DISPLAY_DC, machine.Pin.OUT)
        rst = machine.Pin(DISPLAY_RST, machine.Pin.OUT)
        
        print(f"  Testing CS pin (GPIO {DISPLAY_CS})...")
        cs.value(1)
        time.sleep_ms(10)
        cs.value(0)
        time.sleep_ms(10)
        cs.value(1)
        print(f"  ✓ CS pin: OK")
        
        print(f"  Testing DC pin (GPIO {DISPLAY_DC})...")
        dc.value(1)
        time.sleep_ms(10)
        dc.value(0)
        time.sleep_ms(10)
        print(f"  ✓ DC pin: OK")
        
        print(f"  Testing RST pin (GPIO {DISPLAY_RST})...")
        rst.value(1)
        time.sleep_ms(10)
        rst.value(0)
        time.sleep_ms(10)
        rst.value(1)
        print(f"  ✓ RST pin: OK")
        
        return cs, dc, rst
    except Exception as e:
        print(f"  ✗ Display pin test FAILED: {e}")
        return None, None, None

def test_4_display_init(spi):
    """Test 4: Initialize ST7735S display"""
    print("\n" + "="*50)
    print("TEST 4: ST7735S Display Initialization")
    print("="*50)
    
    if spi is None:
        print("  ✗ Skipping - SPI bus not available")
        return None
    
    try:
        from lib.st7735s import ST7735S
        
        # Increase baudrate for display
        spi.init(baudrate=10000000)
        
        display = ST7735S(
            spi,
            cs=machine.Pin(DISPLAY_CS, machine.Pin.OUT),
            dc=machine.Pin(DISPLAY_DC, machine.Pin.OUT),
            rst=machine.Pin(DISPLAY_RST, machine.Pin.OUT),
            width=128,
            height=160,
            rotation=0
        )
        
        print(f"  ✓ Display initialized")
        print(f"    Width: {display.width}")
        print(f"    Height: {display.height}")
        
        # Try to fill screen
        print(f"  Testing screen fill...")
        display.fill(0xFFFF)  # White
        time.sleep(0.5)
        display.fill(0x0000)  # Black
        print(f"  ✓ Screen fill test: OK")
        
        # Reset baudrate for NFC
        spi.init(baudrate=1000000)
        
        return display
    except Exception as e:
        print(f"  ✗ Display initialization FAILED: {e}")
        import sys
        sys.print_exception(e)
        spi.init(baudrate=1000000)
        return None

def test_5_nfc_pins():
    """Test 5: Test NFC CS pins"""
    print("\n" + "="*50)
    print("TEST 5: NFC CS Pin Control")
    print("="*50)
    
    cs_pins = []
    for i, pin_num in enumerate(NFC_CS_PINS):
        try:
            cs = machine.Pin(pin_num, machine.Pin.OUT)
            cs.value(1)  # Deselect
            time.sleep_ms(10)
            cs.value(0)  # Select
            time.sleep_ms(10)
            cs.value(1)  # Deselect
            print(f"  ✓ NFC Reader {i} CS (GPIO {pin_num}): OK")
            cs_pins.append(cs)
        except Exception as e:
            print(f"  ✗ NFC Reader {i} CS (GPIO {pin_num}): FAILED - {e}")
            cs_pins.append(None)
    
    return cs_pins

def test_6_nfc_init(spi, cs_pins):
    """Test 6: Initialize PN532 NFC readers"""
    print("\n" + "="*50)
    print("TEST 6: PN532 NFC Reader Initialization")
    print("="*50)
    
    if spi is None:
        print("  ✗ Skipping - SPI bus not available")
        return {}
    
    nfc_readers = {}
    
    for i, cs_pin in enumerate(cs_pins):
        if cs_pin is None:
            print(f"  ✗ Reader {i}: Skipping - CS pin failed")
            continue
        
        try:
            print(f"  Initializing Reader {i} on GPIO {NFC_CS_PINS[i]}...")
            
            from pn532.spi import PN532_SPI
            
            # Try with debug enabled
            reader = PN532_SPI(spi, cs_pin=cs_pin, debug=True)
            
            print(f"    Attempting to read firmware version...")
            version = reader.firmware_version
            print(f"  ✓ Reader {i}: OK - Firmware v{version}")
            nfc_readers[i] = reader
            
        except Exception as e:
            print(f"  ✗ Reader {i}: FAILED - {e}")
            import sys
            sys.print_exception(e)
    
    return nfc_readers

def test_7_dip_switches():
    """Test 7: Read DIP switches"""
    print("\n" + "="*50)
    print("TEST 7: DIP Switch Reading")
    print("="*50)
    
    try:
        dip_pins = []
        for pin_num in DIP_PINS:
            pin = machine.Pin(pin_num, machine.Pin.IN, machine.Pin.PULL_UP)
            dip_pins.append(pin)
        
        value = 0
        for i, pin in enumerate(dip_pins):
            bit_val = 0 if pin.value() == 0 else 1  # Active low
            value |= ((1 - bit_val) << i)
            status = "ON" if pin.value() == 0 else "OFF"
            print(f"  DIP {i+1} (GPIO {DIP_PINS[i]}): {status}")
        
        print(f"  ✓ DIP switch value: {value} (binary: {bin(value)})")
        return value
    except Exception as e:
        print(f"  ✗ DIP switch test FAILED: {e}")
        return 0

def main():
    print("\n" + "="*60)
    print("ESP32 NFC CONTROLLER - HARDWARE DEBUG")
    print("="*60)
    print("\nThis script will test each hardware component individually")
    print("to identify which parts are working.\n")
    
    # Run all tests
    test_1_gpio_pins()
    spi = test_2_spi_bus()
    cs, dc, rst = test_3_display_pins()
    display = test_4_display_init(spi)
    cs_pins = test_5_nfc_pins()
    nfc_readers = test_6_nfc_init(spi, cs_pins)
    dip_value = test_7_dip_switches()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"SPI Bus: {'✓ OK' if spi else '✗ FAILED'}")
    print(f"Display: {'✓ OK' if display else '✗ FAILED'}")
    print(f"NFC Readers: {len(nfc_readers)}/{len(NFC_CS_PINS)} detected")
    print(f"DIP Switches: ✓ OK (value={dip_value})")
    print("="*60)
    
    if not spi:
        print("\n⚠ SPI BUS FAILED - Check wiring:")
        print(f"  - SCK:  GPIO {SPI_CLK}")
        print(f"  - MOSI: GPIO {SPI_MOSI}")
        print(f"  - MISO: GPIO {SPI_MISO}")
    
    if not display:
        print("\n⚠ DISPLAY FAILED - Check:")
        print(f"  - CS:  GPIO {DISPLAY_CS}")
        print(f"  - DC:  GPIO {DISPLAY_DC}")
        print(f"  - RST: GPIO {DISPLAY_RST}")
        print(f"  - Power: 3.3V connected?")
    
    if len(nfc_readers) == 0:
        print("\n⚠ NO NFC READERS DETECTED - Check:")
        print("  - PN532 modules in SPI mode (switches set correctly)")
        print("  - CS pins connected to GPIO: " + str(NFC_CS_PINS))
        print("  - Power: 3.3V to all modules")
        print("  - Common ground")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDebug interrupted by user")
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import sys
        sys.print_exception(e)
