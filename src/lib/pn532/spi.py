"""
``pn532.spi``
====================================================

This module will let you communicate with a PN532 RFID/NFC shield or breakout
using SPI.

* Author(s): Adapted from monolithic SPI implementation

Note on CS Pin Management:
- Pass cs_pin for automatic CS management (simple use case)
- Pass cs_pin=None for manual CS management (shared SPI bus with multiple devices)
  When using manual CS management, you must control the CS pin externally before
  calling any PN532 methods.

"""

import time
from micropython import const
from pn532.pn532 import PN532, BusyError

_SPI_STATREAD = const(0x02)
_SPI_DATAWRITE = const(0x01)
_SPI_DATAREAD = const(0x03)
_SPI_READY = const(0x01)


def _reverse_bit(num):
    """Turn an LSB byte to an MSB byte, and vice versa. Used for SPI as
    it is LSB for the PN532, but 99% of SPI implementations are MSB only!"""
    result = 0
    for _ in range(8):
        result <<= 1
        result += (num & 1)
        num >>= 1
    return result


class PN532_SPI(PN532):
    """Driver for the PN532 connected over SPI.
    
    Args:
        spi: SPI bus object (machine.SPI)
        cs_pin: Optional chip select pin. If None, CS must be managed externally.
        irq: Optional IRQ pin (not currently used)
        reset: Optional reset pin
        debug: Enable debug output
        
    Example (automatic CS):
        spi = SPI(1, baudrate=1000000, polarity=0, phase=0)
        cs = Pin(13, Pin.OUT)
        nfc = PN532_SPI(spi, cs_pin=cs, reset=Pin(27))
        
    Example (manual CS for shared bus):
        spi = SPI(1, baudrate=1000000, polarity=0, phase=0)
        cs1 = Pin(13, Pin.OUT)
        cs1.value(1)  # Deselect initially
        nfc = PN532_SPI(spi, cs_pin=None, reset=Pin(27))
        # Then before each operation:
        cs1.value(0)
        nfc.read_passive_target()
        cs1.value(1)
    """

    def __init__(self, spi, cs_pin=None, *, irq=None, reset=None, debug=False):
        """Create an instance of the PN532 class using SPI connection.
        Optional CS pin, reset pin and debugging output.
        """
        self.debug = debug
        self._spi = spi
        self._cs = cs_pin
        self._manage_cs = cs_pin is not None
        
        # Initialize CS pin if we're managing it
        if self._manage_cs:
            self._cs.value(1)  # Deselect initially
            
        super().__init__(irq=irq, reset=reset, debug=debug)

    def _cs_low(self):
        """Assert CS (select device) if we're managing it"""
        if self._manage_cs:
            self._cs.value(0)
            time.sleep_ms(2)

    def _cs_high(self):
        """Deassert CS (deselect device) if we're managing it"""
        if self._manage_cs:
            time.sleep_ms(2)
            self._cs.value(1)

    def _wakeup(self):
        """Send any special commands/data to wake up PN532"""
        if self._reset_pin:
            self._reset_pin.on()
            time.sleep(0.01)
        self.low_power = False
        time.sleep(1)
        self._cs_low()
        self._spi.write(bytearray([0x00]))
        self._cs_high()
        time.sleep(1)

    def _wait_ready(self, timeout=1000):
        """Poll PN532 if status byte is ready, up to `timeout` milliseconds"""
        status_query = bytearray([_reverse_bit(_SPI_STATREAD), 0])
        status = bytearray([0, 0])
        timestamp = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), timestamp) < timeout:
            time.sleep(0.02)
            self._cs_low()
            self._spi.write_readinto(status_query, status)
            self._cs_high()
            if _reverse_bit(status[1]) == _SPI_READY:
                return True
            time.sleep(0.01)
        return False

    def _read_data(self, count):
        """Read a specified count of bytes from the PN532."""
        frame = bytearray(count + 1)
        frame[0] = _reverse_bit(_SPI_DATAREAD)
        time.sleep(0.02)
        self._cs_low()
        self._spi.write_readinto(frame, frame)
        self._cs_high()
        
        # Convert from LSB to MSB
        for i, val in enumerate(frame):
            frame[i] = _reverse_bit(val)
            
        if self.debug:
            print("Reading: ", [hex(i) for i in frame[1:]])
        return frame[1:]  # Don't return the status byte

    def _write_data(self, framebytes):
        """Write a specified count of bytes to the PN532"""
        # Build frame with data write command, then convert to LSB
        rev_frame = [_reverse_bit(x) for x in bytes([_SPI_DATAWRITE]) + framebytes]
        
        if self.debug:
            print("Writing: ", [hex(i) for i in rev_frame])
            
        time.sleep(0.02)
        self._cs_low()
        self._spi.write(bytes(rev_frame))
        self._cs_high()
