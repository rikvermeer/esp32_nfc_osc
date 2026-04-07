import time
import json
import machine
from config import load_config, DEFAULT_CONFIG, config_exists
from wifi_manager import connect_wifi, start_access_point
from hardware_spi import (
    scan_hardware,
    read_nfc_tag,
    print_display,
    update_display_dashboard,
    show_status_screen,
    get_track_ids_for_reader,
    read_dip_switches
)
from osc_client import OSCClient
from setup_portal import run_setup_portal

# Setup button configuration (GPIO pin with pull-up)
SETUP_BUTTON_PIN = 0  # Boot button on most ESP32 boards

def load_tag_mapping():
    """Load NFC tag to track mapping from JSON file"""
    try:
        with open('/mapping.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading mapping: {e}")
        return {}


def is_setup_button_pressed():
    """Check if setup button is pressed"""
    try:
        setup_button = machine.Pin(SETUP_BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
        return setup_button.value() == 0
    except Exception as e:
        print(f"Error reading setup button: {e}")
        return False

def should_enter_setup_mode(config):
    """Determine if device should enter setup mode"""
    # Check if setup button is pressed
    if is_setup_button_pressed():
        print("Setup button pressed - entering setup mode")
        return True
    
    # Check if essential config is missing
    if not config.get('wifi_ssid') or not config.get('osc_server_ip'):
        print("Essential config missing - entering setup mode")
        return True
    
    return False

def run_setup_mode(config):
    """Run setup mode: start AP and web portal"""
    print("=== ENTERING SETUP MODE ===")
    
    # Initialize display for setup mode
    from hardware_spi import init_spi, init_display
    init_spi()
    display = init_display()
    
    # Show setup mode status
    if display:
        try:
            show_status_screen(
                mode="setup",
                wifi_status=None,
                wifi_ssid=None,
                osc_status=None,
                osc_ip=None,
                reader_states=None
            )
        except:
            pass
    
    ap = start_access_point(config.get('ap_ssid', 'NFC-SETUP'), 
                           config.get('ap_password', '12345678'))
    run_setup_portal(ap)

def run_application(config):
    """Run normal application mode"""
    print("=== ENTERING APPLICATION MODE ===")
    
    # Initialize display first to show boot progress
    from hardware_spi import init_spi, init_display
    print("Initializing SPI bus...")
    init_spi()
    print("Initializing display...")
    display = init_display()
    
    # Show boot screen
    if display:
        import st7789
        try:
            display.fill(st7789.BLACK)
            # Draw boot indicator
            display.fill_rect(10, 70, 108, 20, st7789.GREEN)
            print("Display initialized successfully!")
        except Exception as e:
            print(f"Display test failed: {e}")
            display = None
    else:
        print("Display not available - continuing without display")
    
    # Scan and initialize hardware (SPI-based NFC readers)
    nfc_readers, _ = scan_hardware()
    
    # Show initial status: connecting to WiFi
    if display:
        try:
            show_status_screen(
                mode="application",
                wifi_status="connecting",
                wifi_ssid=config['wifi_ssid'],
                osc_status=None,
                osc_ip=None,
                reader_states=None
            )
        except:
            pass
    
    # Read DIP switch configuration
    dip_config = read_dip_switches()
    print(f"DIP switch configuration: {dip_config}")
    
    # Load tag mapping
    mapping = load_tag_mapping()
    print("\nMapping:")
    print(mapping)
    print("\n")
    
    # Connect to WiFi
    wlan = connect_wifi(config['wifi_ssid'], config['wifi_password'])
    
    # Check if WiFi connection failed
    if wlan is None:
        print("WiFi connection failed - entering setup mode")
        if display:
            try:
                show_status_screen(
                    mode="application",
                    wifi_status="failed",
                    wifi_ssid=config['wifi_ssid'],
                    osc_status=None,
                    osc_ip=None,
                    reader_states=None
                )
            except:
                pass
            time.sleep(2)
        run_setup_mode(config)
        return
    
    # Show WiFi connected status
    if display:
        try:
            show_status_screen(
                mode="application",
                wifi_status="connected",
                wifi_ssid=config['wifi_ssid'],
                osc_status="ready",
                osc_ip=config['osc_server_ip'],
                reader_states=None
            )
        except:
            pass
    
    # Initialize OSC client
    osc = OSCClient(config['osc_server_ip'], config['osc_server_port'])
    
    # Initialize display with all readers empty
    if display:
        initial_states = {}
        for reader_index in nfc_readers.keys():
            initial_states[reader_index] = {
                'has_tag': False,
                'tag_id': None,
                'track_id': None
            }
        try:
            show_status_screen(
                mode="application",
                wifi_status="connected",
                wifi_ssid=config['wifi_ssid'],
                osc_status="ready",
                osc_ip=config['osc_server_ip'],
                reader_states=initial_states
            )
        except:
            pass
    
    try:
        # Main loop
        previous_states = {}
        while True:
            reader_states = {}
            
            # Iterate over each NFC reader and collect states
            for reader_index, nfc_reader in nfc_readers.items():
                print(f"Checking NFC reader {reader_index}...")
                
                # Read NFC tag
                uid = read_nfc_tag(nfc_reader, reader_index)
                track_ids = get_track_ids_for_reader(reader_index)
                tag_id = None
                track_id = None
                
                if uid:
                    tag_id = mapping.get(uid, None)
                    if tag_id is None:
                        print(f"Tag id not found for uid: {uid}")
                        reader_states[reader_index] = {
                            'has_tag': True,
                            'tag_id': None,
                            'track_id': None
                        }
                    else:
                        print(f"Reader {reader_index}: UID={uid}, Tag={tag_id}")
                        osc.stop_tracks(track_ids)
                        track_id = track_ids[tag_id]
                        osc.fire_clip(track_id)
                        
                        reader_states[reader_index] = {
                            'has_tag': True,
                            'tag_id': tag_id,
                            'track_id': track_id
                        }
                else:
                    osc.stop_tracks(track_ids)
                    reader_states[reader_index] = {
                        'has_tag': False,
                        'tag_id': None,
                        'track_id': None
                    }
            
            # Update display only if states have changed
            if display and reader_states != previous_states:
                try:
                    show_status_screen(
                        mode="application",
                        wifi_status="connected",
                        wifi_ssid=config['wifi_ssid'],
                        osc_status="ready",
                        osc_ip=config['osc_server_ip'],
                        reader_states=reader_states
                    )
                    previous_states = reader_states.copy()
                    print("Display updated")
                except Exception as display_error:
                    print(f"Display update failed: {display_error}")
                    display = None
            
            # Sleep to avoid busy waiting
            time.sleep_ms(50)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        osc.close()
    except Exception as e:
        print(f"Error in main loop: {e}")
        import sys
        sys.print_exception(e)
        osc.close()

def main():
    # Load configuration from file or use defaults
    config = load_config()
    print(f"Using config: WiFi={config['wifi_ssid']}, OSC={config['osc_server_ip']}:{config['osc_server_port']}")
    
    # Check if we should enter setup mode
    if should_enter_setup_mode(config):
        run_setup_mode(config)
    else:
        run_application(config)

if __name__ == "__main__":
    main()
