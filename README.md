# ESP32 NFC Controller for AbletonOSC

This project enables an ESP32 to read multiple NFC readers connected via an I2C multiplexer and send OSC messages to AbletonOSC for interactive control of Ableton Live.

## Hardware Requirements

- ESP32 development board
- TCA9548A I2C Multiplexer
- PN532 NFC readers (up to 8, one per multiplexer channel)
- Jumper wires
- Breadboard
- USB cable for programming and power

## Wiring

### ESP32 to TCA9548A
- ESP32 GND → TCA9548A GND
- ESP32 3.3V → TCA9548A VCC
- ESP32 SCL (GPIO 22) → TCA9548A SCL
- ESP32 SDA (GPIO 21) → TCA9548A SDA

### TCA9548A to PN532 Readers
For each PN532 NFC reader:
- TCA9548A SDx → PN532 SDA
- TCA9548A SCx → PN532 SCL
- TCA9548A VCC → PN532 VCC
- TCA9548A GND → PN532 GND

## Setup

1. **Install MicroPython on ESP32**
   - Download the latest MicroPython firmware for ESP32 from [micropython.org](https://micropython.org/download/esp32/)
   - Flash it using esptool or Thonny IDE

2. **Install required libraries**
   - Copy the `umqtt` and `uosc` libraries to your ESP32's `/lib` directory
   - Or install using upip if you have internet connectivity:
     ```
     import upip
     upip.install('micropython-umqtt.simple')
     upip.install('micropython-uosc')
     ```

3. **Configure WiFi and OSC settings**
   - Edit `main.py` and update these variables:
     - `WIFI_SSID`: Your WiFi network name
     - `WIFI_PASSWORD`: Your WiFi password
     - `OSC_SERVER_IP`: IP address of the computer running AbletonOSC
     - `OSC_SERVER_PORT`: Port for AbletonOSC (default: 11000)

4. **Upload code to ESP32**
   - Upload `main.py` to your ESP32 as `main.py`
   - The ESP32 will automatically run this script on boot

## Using with AbletonOSC

1. Make sure AbletonOSC is properly installed in your Ableton Live's Remote Scripts folder
2. Start Ableton Live and enable the AbletonOSC control surface in Live's preferences
3. The ESP32 will send OSC messages in the format `/nfc/reader/{channel} {uid}` when an NFC tag is detected

## Customizing OSC Messages

You can modify the `send_osc_message()` function in `main.py` to send different OSC messages based on the detected UID. For example, you could map specific UIDs to specific Ableton actions.

## Troubleshooting

- Check the serial console for error messages
- Verify all connections are correct and secure
- Ensure the I2C addresses match your hardware configuration
- Make sure AbletonOSC is running and the IP/port are correctly configured

## License

MIT
