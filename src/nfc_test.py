"""
NFC Reader Test Script
Test all 4 PN532 NFC readers on shared SPI bus

Pin Configuration:
- SPI Bus: MOSI=23, MISO=19, CLK=18
- NFC CS pins: 13, 16, 32, 22
"""

import time
from hardware_spi import (
    scan_hardware,
    read_nfc_tag,
    read_dip_switches,
    get_track_ids_for_reader
)

def main():
    print("="*50)
    print("NFC Reader Test - SPI Mode")
    print("="*50)
    
    # Initialize hardware
    print("\nInitializing hardware...")
    nfc_readers, display = scan_hardware()
    
    if not nfc_readers:
        print("ERROR: No NFC readers found!")
        print("Check wiring and SPI connections.")
        return
    
    print(f"\nFound {len(nfc_readers)} NFC reader(s)")
    print(f"Display: {'initialized' if display else 'not found'}")
    
    # Read DIP switches
    dip_value = read_dip_switches()
    print(f"DIP switch value: {dip_value} (binary: {bin(dip_value)})")
    
    print("\n" + "="*50)
    print("Starting continuous NFC scan...")
    print("Place NFC tags near readers to test")
    print("Press Ctrl+C to stop")
    print("="*50 + "\n")
    
    last_uids = {i: None for i in nfc_readers.keys()}
    
    try:
        while True:
            for reader_index, nfc_reader in nfc_readers.items():
                # Read NFC tag
                uid = read_nfc_tag(nfc_reader, reader_index)
                
                # Only print if UID changed
                if uid != last_uids[reader_index]:
                    last_uids[reader_index] = uid
                    
                    if uid:
                        track_ids = get_track_ids_for_reader(reader_index)
                        print(f"[Reader {reader_index}] Tag detected!")
                        print(f"  UID: {uid}")
                        print(f"  Track IDs: {track_ids}")
                    else:
                        print(f"[Reader {reader_index}] Tag removed")
            
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("\n\nTest stopped by user")
        print("\nSummary:")
        for i, uid in last_uids.items():
            status = f"UID: {uid}" if uid else "No tag"
            print(f"  Reader {i}: {status}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        import sys
        sys.print_exception(e)
