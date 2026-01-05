"""
``pn532.i2c``
====================================================

This module will let you communicate with a PN532 RFID/NFC shield or breakout
using I2C.

* Author(s): Adapted from UART implementation by [Your Name]

"""

import time
from pn532.pn532 import PN532, BusyError

PN532_I2C_ADDR = 0x24

class PN532_I2C(PN532):
    """Driver for the PN532 connected over I2C"""

    def __init__(self, i2c, addr=PN532_I2C_ADDR, *, irq=None, reset=None, debug=False):
        """Create an instance of the PN532 class using I2C connection.
        Optional reset pin and debugging output.
        """
        self.debug = debug
        self._i2c = i2c
        self._addr = addr
        super().__init__(irq=irq, reset=reset, debug=debug)

    def _wakeup(self):
        """Send any special commands/data to wake up PN532"""
        if self._reset_pin:
            self._reset_pin.on()
            time.sleep(0.01)
        self.low_power = False
        # I2C wakeup sequence
        self._i2c.writeto(self._addr, b"\x55\x55\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        time.sleep(.1)
        self.SAM_configuration()

    def _wait_ready(self, timeout=2000):
        """Wait `timeout` milliseconds for the PN532 to be ready."""
        start = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start) < timeout:
            try:
                # Send a command to check readiness, e.g., a status register read
                #self._i2c.writeto(self._addr, b'\x00')  # Example command
                response = self._i2c.readfrom(self._addr, 1)
                if self.debug:
                    print("Wait ready: ", [hex(i) for i in response])
                if response == b'\x01':  # Example expected response
                    if self.debug:
                        print("Device is ready")
                    return True  # Device is ready
            except OSError as e:
                if self.debug:
                    print("I2C read error: ", e)
                pass  # Handle I2C errors if necessary
            time.sleep(0.01)  # Wait a bit before retrying
        # Timed out!
        return False

    def _read_data(self, count):
        """Read a specified count of bytes from the PN532 over I2C."""
        frame = self._i2c.readfrom(self._addr, count+1)
        #print("Reading: ", [hex(i) for i in frame])
        if not frame:
            raise BusyError("No data read from PN532")
        #print("frame[0]: ", hex(frame[0]))
        if frame[0] != 0x01:
            raise BusyError("frame[0] != b'\x01'")
        frame = frame[1:]
        if self.debug:
            print("Reading: ", [hex(i) for i in frame])
        return frame

    def _write_data(self, framebytes):
        """Write a specified count of bytes to the PN532 over I2C"""
        if self.debug:
            print("Writing: ", [hex(i) for i in framebytes])
        try:
            self._i2c.writeto(self._addr, bytes(framebytes))
        except OSError as e:
            if self.debug:
                print("I2C write error: ", e)
            raise
