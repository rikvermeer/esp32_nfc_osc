# ESP32 NFC Controller for AbletonOSC

This project enables an ESP32 to read multiple NFC readers connected via SPI and send OSC messages to AbletonOSC for interactive control of Ableton Live.

## Hardware Requirements

- ESP32 DevKit C v4
- 4x PN532 NFC readers (SPI mode)
- ST7735S LCD display
- 3-bit DIP switch
- Jumper wires
- Breadboard
- USB cable for programming and power

## Wiring

### SPI Bus (Shared)
- ESP32 GPIO 23 (MOSI) → All PN532 MOSI & ST7735S SDA
- ESP32 GPIO 19 (MISO) → All PN532 MISO
- ESP32 GPIO 18 (CLK) → All PN532 SCK & ST7735S SCL
- ESP32 3.3V → All PN532 VCC & ST7735S VCC
- ESP32 GND → All PN532 GND & ST7735S GND

### PN532 NFC Readers (Chip Select pins)
- ESP32 GPIO 32 → PN532 #1 SS
- ESP32 GPIO 22 → PN532 #2 SS
- ESP32 GPIO 13 → PN532 #3 SS
- ESP32 GPIO 4 → PN532 #4 SS

### ST7735S LCD Display
- ESP32 GPIO 21 → ST7735S CS (Chip Select)
- ESP32 GPIO 17 → ST7735S DC (Data/Command)
- ESP32 GPIO 16 → ST7735S RST (Reset)
- ESP32 3.3V → ST7735S BL (Backlight)

### DIP Switch (3-bit)
- ESP32 GPIO 26 → DIP switch bit 1
- ESP32 GPIO 25 → DIP switch bit 2
- ESP32 GPIO 33 → DIP switch bit 3
- DIP switch common → ESP32 GND (with pull-up resistors on GPIO pins)

## Setup

1. **Install MicroPython on ESP32**
   - Download the latest MicroPython firmware for ESP32 from [micropython.org](https://micropython.org/download/esp32/)
   - Flash it using esptool or Thonny IDE
   - ```python -m esptool --chip esp32 --port COM4 --baud 460800 write-flash -z 0x1000 esp32_nfc_controller\firmware\firmware-russhughes-st7789_mpy.bin```
   - ```py -3.11 -m esptool --chip esp32 --port COM4 --baud 460800 write-flash -z 0x1000 esp32_nfc_controller\firmware\firmware-russhughes-st7789_mpy.bin```



2. **Upload code to ESP32**
   - Upload all files from the `src/` directory to your ESP32
   - - ```py -3.11 -m mpremote connect COM4 fs cp -r esp32_nfc_controller\src :/``` 
   - Upload `mapping.json`  or `mapping.json.example` with your NFC tag mappings
   - - ```py -3.11 -m mpremote connect COM4 fs cp esp32_nfc_controller\src\mapping.json.example :/mapping.json```
   - Upload `config.json`  or `config.json.example` with your WiFi / OSC ip settings
   - - ```py -3.11 -m mpremote connect COM4 fs cp esp32_nfc_controller\src\config.json.example :/config.json```     

3. **Initial Configuration via Web Interface**
   - On first boot (or when setup button is pressed), the ESP32 enters setup mode
   - Connect to WiFi network `NFC-SETUP` (no password)
   - Open browser and navigate to `http://192.168.4.1`
   - Configure your settings:
     - **WiFi SSID**: Your WiFi network name
     - **WiFi Password**: Your WiFi password
     - **OSC Server IP**: IP address of computer running AbletonOSC
     - **OSC Server Port**: Port for AbletonOSC (default: 11000)
   - Click "Save & Reboot"
   - ESP32 will save config to `/config.json` and restart in normal mode

## Configuration

### Setup Mode
The ESP32 enters setup mode when:
- Setup button (GPIO 0, boot button) is pressed during boot
- WiFi connection fails
- Config file is missing or incomplete

In setup mode, the ESP32 creates an access point and web server for configuration.

### Normal Mode
After successful configuration, the ESP32:
- Connects to configured WiFi network
- Initializes SPI bus and 4 NFC readers
- Reads NFC tags and sends OSC messages to Ableton Live
- Shows status on ST7735S LCD display
- Reads DIP switch settings for configuration

### Reconfiguration
To reconfigure the device:
- Hold the boot button (GPIO 0) while powering on the ESP32
- Or delete `/config.json` file from the ESP32 filesystem

## Using with AbletonOSC

1. Make sure AbletonOSC is properly installed in your Ableton Live's Remote Scripts folder
2. Start Ableton Live and enable the AbletonOSC control surface in Live's preferences
3. The ESP32 will send OSC messages in the format `/live/clip/fire {track_id} {clip_id}` when an NFC tag is detected

## Customizing OSC Messages

You can modify the `send_osc_message()` function in `main.py` to send different OSC messages based on the detected UID. For example, you could map specific UIDs to specific Ableton actions.
The mapping is done in the `mapping.json` file.

## Troubleshooting
- WiFi must be working. Verify all connections are correct and secure
- Make sure AbletonOSC is running and the IP/port are correctly configured
- Check the serial console for error messages
- Reboot the device if one of the NFC readers doesn't work.
