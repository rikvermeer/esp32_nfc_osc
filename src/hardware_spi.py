"""
Hardware abstraction layer for SPI-based NFC readers and ST7789 display

Architecture:
- 4x PN532 NFC readers on shared SPI bus with individual CS pins
- 1x ST7789 display on shared SPI bus
- 3-bit DIP switch for configuration
"""

import machine
import time
import binascii
from pn532.spi import PN532_SPI
import st7789
try:
    import vga1_8x16 as font_small
    import vga1_16x16 as font_medium
    FONTS_AVAILABLE = True
except ImportError:
    FONTS_AVAILABLE = False
    print("Warning: Display fonts not available")

DEBUG = False

# Pin definitions
SPI_MOSI = 23
SPI_MISO = 19
SPI_CLK = 18

# NFC CS pins
NFC_CS_PINS = [32, 22, 13, 4]

# Display pins
DISPLAY_CS = 21
DISPLAY_DC = 17
DISPLAY_RST = 16

# DIP switch pins
DIP_PINS = [26, 25, 33]

# Display dimensions
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 160

# Global variables
spi = None
nfc_cs_pins = []
display = None
dip_switches = []


def init_spi():
    """Initialize shared SPI bus"""
    global spi
    spi = machine.SPI(
        1,
        baudrate=1000000,  # 1 MHz for PN532 (conservative)
        polarity=0,
        phase=0,
        sck=machine.Pin(SPI_CLK),
        mosi=machine.Pin(SPI_MOSI),
        miso=machine.Pin(SPI_MISO)
    )
    print("SPI bus initialized")
    return spi


def init_dip_switches():
    """Initialize DIP switch pins with pull-up resistors"""
    global dip_switches
    dip_switches = []
    for pin_num in DIP_PINS:
        pin = machine.Pin(pin_num, machine.Pin.IN, machine.Pin.PULL_UP)
        dip_switches.append(pin)
    print(f"DIP switches initialized on pins {DIP_PINS}")
    return dip_switches


def read_dip_switches():
    """Read DIP switch values and return as integer (0-7)"""
    if not dip_switches:
        init_dip_switches()
    
    value = 0
    for i, pin in enumerate(dip_switches):
        # DIP switch is active low (0 = ON, 1 = OFF)
        if pin.value() == 0:
            value |= (1 << i)
    return value


def init_display():
    """Initialize ST7789 display"""
    global display
    
    if spi is None:
        init_spi()
    
    try:
        # Increase SPI speed for display (10 MHz for stability)
        spi.init(baudrate=10000000)
        
        display = st7789.ST7789(
            spi,
            DISPLAY_WIDTH,
            DISPLAY_HEIGHT,
            reset=machine.Pin(DISPLAY_RST, machine.Pin.OUT),
            cs=machine.Pin(DISPLAY_CS, machine.Pin.OUT),
            dc=machine.Pin(DISPLAY_DC, machine.Pin.OUT),
            inversion=False,
            rotation=0
        )
        display.init()
        
        # Reset SPI speed back to 1 MHz for NFC
        spi.init(baudrate=1000000)
        
        print("Display initialized")
        return display
    except Exception as e:
        print(f"Error initializing display: {e}")
        import sys
        sys.print_exception(e)
        return None


def scan_hardware():
    """Initialize all NFC readers on SPI bus with manual CS control"""
    global nfc_cs_pins
    
    if spi is None:
        init_spi()
    
    nfc_readers = {}
    
    # Initialize CS pins for all NFC readers
    nfc_cs_pins = []
    for pin_num in NFC_CS_PINS:
        cs_pin = machine.Pin(pin_num, machine.Pin.OUT)
        cs_pin.value(1)  # Deselect initially
        nfc_cs_pins.append(cs_pin)
    
    # Try to initialize each NFC reader
    for i, cs_pin in enumerate(nfc_cs_pins):
        try:
            print(f"Initializing NFC reader {i} on CS pin {NFC_CS_PINS[i]}...")
            
            # Create PN532 instance with automatic CS management
            # The PN532 needs to control CS during wakeup/initialization
            reader = PN532_SPI(spi, cs_pin=cs_pin, debug=DEBUG)
            
            # Try to get firmware version to verify it works
            try:
                version = reader.firmware_version
                print(f"  NFC reader {i} found: firmware v{version}")
                reader.SAM_configuration()
                print(f"  NFC reader {i} SAM configured")
                nfc_readers[i] = reader
                time.sleep_ms(200)
            except Exception as e:
                print(f"  NFC reader {i} not responding: {e}")
            
        except Exception as e:
            print(f"  Error initializing NFC reader {i}: {e}")
    
    # Initialize display (optional)
    display_obj = init_display()
    
    # Initialize DIP switches
    init_dip_switches()
    dip_value = read_dip_switches()
    print(f"DIP switch value: {dip_value}")
    
    print(f"\nFound {len(nfc_readers)} NFC readers")
    return nfc_readers, display_obj


def select_reader(reader_index):
    """Select specific NFC reader by asserting its CS pin"""
    if reader_index < 0 or reader_index >= len(nfc_cs_pins):
        return
    
    # Deselect all readers first
    for cs_pin in nfc_cs_pins:
        cs_pin.value(1)
    
    # Select the requested reader
    nfc_cs_pins[reader_index].value(0)
    time.sleep_ms(2)


def deselect_all_readers():
    """Deselect all NFC readers"""
    for cs_pin in nfc_cs_pins:
        cs_pin.value(1)


def read_nfc_tag(nfc_reader, reader_index):
    """Read NFC tag and return UID as hex string"""
    try:
        # PN532_SPI handles CS automatically now
        uid = nfc_reader.read_passive_target(timeout=100)
        
        if uid:
            hex_uid = binascii.hexlify(uid).decode('utf-8')
            if DEBUG:
                print(f"Reader {reader_index} - UID: {hex_uid}")
            return hex_uid
        else:
            return None
    except Exception as e:
        if DEBUG:
            print(f"Error reading NFC tag on reader {reader_index}: {e}")
        return None


def update_display_dashboard(reader_states):
    """
    Update display with visual dashboard showing all 4 readers
    
    reader_states: dict with reader_index as key and state dict as value
        state = {
            'has_tag': bool,
            'tag_id': int or None,
            'track_id': int or None
        }
    """
    global display, spi
    
    if display is None or spi is None:
        return
    
    try:
        # Increase SPI speed for display
        spi.init(baudrate=10000000)
        
        # Clear display
        display.fill(st7789.BLACK)
        
        # Draw 4 reader zones (2x2 grid)
        zone_width = 64
        zone_height = 80
        
        for i in range(4):
            x = (i % 2) * zone_width
            y = (i // 2) * zone_height
            
            state = reader_states.get(i, {'has_tag': False, 'tag_id': None, 'track_id': None})
            
            # Determine color based on state
            if state.get('has_tag'):
                color = st7789.GREEN if state.get('track_id') is not None else st7789.BLUE
                border_color = st7789.WHITE
            else:
                color = st7789.BLACK
                border_color = st7789.RED
            
            # Draw zone border
            display.rect(x, y, zone_width, zone_height, border_color)
            
            # Draw filled indicator
            if state.get('has_tag'):
                # Large filled circle-like rectangle
                display.fill_rect(x + 18, y + 25, 28, 30, color)
            
            # Draw reader number indicator (small corner marker)
            marker_size = 12
            display.fill_rect(x + 2, y + 2, marker_size, marker_size, st7789.WHITE if i == 0 else st7789.RED if i == 1 else st7789.GREEN if i == 2 else st7789.BLUE)
        
        # Reset SPI speed for NFC
        spi.init(baudrate=1000000)
        
    except Exception as e:
        print(f"Error updating display dashboard: {e}")
        import sys
        sys.print_exception(e)
        if spi:
            try:
                spi.init(baudrate=1000000)
            except:
                pass


def show_status_screen(mode, wifi_status=None, wifi_ssid=None, osc_status=None, osc_ip=None, reader_states=None):
    """
    Display comprehensive status screen
    
    Args:
        mode: "setup" or "application"
        wifi_status: "connecting", "connected", "failed", None
        wifi_ssid: SSID name or None
        osc_status: "ready", "disconnected", None
        osc_ip: OSC server IP address or None
        reader_states: dict of reader states (same format as update_display_dashboard)
    """
    global display, spi
    
    if display is None or spi is None:
        return
    
    try:
        # Increase SPI speed for display
        spi.init(baudrate=10000000)
        
        # Clear display
        display.fill(st7789.BLACK)
        
        if not FONTS_AVAILABLE:
            # Fallback: show colored bars
            y = 10
            if mode == "setup":
                display.fill_rect(5, y, 118, 12, st7789.YELLOW)
            else:
                display.fill_rect(5, y, 118, 12, st7789.GREEN)
            spi.init(baudrate=1000000)
            return
        
        y = 2
        
        # Title based on mode
        if mode == "setup":
            display.text(font_small, "SETUP MODE", 10, y, st7789.YELLOW, st7789.BLACK)
        else:
            display.text(font_small, "NFC Controller", 5, y, st7789.WHITE, st7789.BLACK)
        
        y += 18
        display.hline(0, y, DISPLAY_WIDTH, st7789.WHITE)
        y += 3
        
        # WiFi status
        if mode == "setup":
            display.text(font_small, "AP:NFC-SETUP", 5, y, st7789.CYAN, st7789.BLACK)
            y += 14
            display.text(font_small, "IP:192.168.4.1", 5, y, st7789.CYAN, st7789.BLACK)
        elif wifi_ssid:
            ssid_short = wifi_ssid[:15] if len(wifi_ssid) > 15 else wifi_ssid
            display.text(font_small, f"WiFi:{ssid_short}", 5, y, st7789.WHITE, st7789.BLACK)
            y += 14
            if wifi_status == "connected":
                display.text(font_small, "Status:OK", 5, y, st7789.GREEN, st7789.BLACK)
            elif wifi_status == "connecting":
                display.text(font_small, "Status:...", 5, y, st7789.YELLOW, st7789.BLACK)
            elif wifi_status == "failed":
                display.text(font_small, "Status:FAIL", 5, y, st7789.RED, st7789.BLACK)
        
        y += 18
        
        # OSC status (only in application mode)
        if mode == "application" and osc_status:
            if osc_status == "ready":
                display.text(font_small, "OSC:Ready", 5, y, st7789.GREEN, st7789.BLACK)
            else:
                display.text(font_small, "OSC:Offline", 5, y, st7789.RED, st7789.BLACK)
            y += 14
            
            # Show OSC server IP
            if osc_ip:
                ip_short = osc_ip[:15] if len(osc_ip) > 15 else osc_ip
                display.text(font_small, f"{ip_short}", 5, y, st7789.CYAN, st7789.BLACK)
            y += 18
        
        # NFC reader states (only if provided)
        if reader_states and mode == "application":
            display.hline(0, y, DISPLAY_WIDTH, st7789.WHITE)
            y += 3
            
            for i in range(4):
                state = reader_states.get(i, {'has_tag': False, 'tag_id': None, 'track_id': None})
                
                if state.get('has_tag'):
                    tag_id = state.get('tag_id')
                    track_id = state.get('track_id')
                    
                    if tag_id is not None and track_id is not None:
                        text = f"{["D", "B", "H", "M"][i]}:T{tag_id}->Tr{track_id}"
                        color = st7789.GREEN
                    else:
                        text = f"{["D", "B", "H", "M"][i]}:Unknown"
                        color = st7789.BLUE
                else:
                    text = f"{["D", "B", "H", "M"][i]}:Empty"
                    color = st7789.CYAN
                
                display.text(font_small, text, 5, y, color, st7789.BLACK)
                y += 14
        
        # Reset SPI speed for NFC
        spi.init(baudrate=1000000)
        
    except Exception as e:
        print(f"Error showing status screen: {e}")
        import sys
        sys.print_exception(e)
        if spi:
            try:
                spi.init(baudrate=1000000)
            except:
                pass


def print_display(text, color=None, bg_color=None):
    """Legacy text display function - draws simple colored bars for text lines"""
    global display
    
    if display is None:
        return
    
    if color is None:
        color = st7789.WHITE
    if bg_color is None:
        bg_color = st7789.BLACK
    
    try:
        spi.init(baudrate=10000000)
        display.fill(bg_color)
        
        lines = text.split('\n')
        y_offset = 10
        for i, line in enumerate(lines[:10]):
            if line.strip():
                display.fill_rect(5, y_offset + (i * 15), 118, 12, color)
        
        spi.init(baudrate=1000000)
    except Exception as e:
        print(f"Error updating display: {e}")
        spi.init(baudrate=1000000)


def get_track_ids_for_reader(reader_index, num_tracks_per_reader=6):
    """Get track IDs for specific NFC reader (default 6 tracks per reader)"""
    track_ids = []
    for i in range(num_tracks_per_reader):
        track_ids.append(reader_index * num_tracks_per_reader + i)
    
    if DEBUG:
        print(f"Track IDs for reader {reader_index}: {track_ids}")
    
    return track_ids
