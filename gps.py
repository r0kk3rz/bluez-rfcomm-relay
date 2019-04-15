# Simple GPS module demonstration.
# Will wait for a fix and print a message every second with the current location
# and other details.
import time
import board
import serial
import RPi.GPIO as GPIO

class GPS:
    def __init__(self):
        self._uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=3000)
        self._fix_quality = None

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23, GPIO.OUT)
        GPIO.output(23, GPIO.LOW)

    def start(self):
        # Enable GPS Module
        GPIO.output(23, GPIO.HIGH)

        # give it a bit to wake up
        time.sleep(3)

        # Turn on the basic GGA and RMC info
        self._send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

        # Turn on just minimum info (RMC only, location):
        # self._send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

        # Set update rate
        self._send_command(b'PMTK220,200')

        time.sleep(2)

    def stop(self):
        GPIO.output(23, GPIO.LOW)

    def update(self):
        return self._parse_sentence()

    def _send_command(self, command, add_checksum=True):
        """Send a command string to the GPS.  If add_checksum is True (the
        default) a NMEA checksum will automatically be computed and added.
        Note you should NOT add the leading $ and trailing * to the command
        as they will automatically be added!
        """
        self._uart.write(b'$')
        self._uart.write(command)
        if add_checksum:
            checksum = 0
            for char in command:
                checksum ^= char
            self._uart.write(b'*')
            self._uart.write(bytes('{:02x}'.format(checksum).upper(), "ascii"))
        self._uart.write(b'\r\n')

    def _parse_sentence(self):
        # Parse any NMEA sentence that is available.
        # pylint: disable=len-as-condition
        sentence = self._uart.readline()
        if sentence is None or sentence == b'' or len(sentence) < 1:
            return None
        
        try:
            sentence = str(sentence, 'ascii').strip()
        except UnicodeDecodeError as e:
            return None
        # Look for a checksum and validate it if present.
        if len(sentence) > 7 and sentence[-3] == '*':
            # Get included checksum, then calculate it and compare.
            expected = int(sentence[-2:], 16)
            actual = 0
            for i in range(1, len(sentence)-3):
                actual ^= ord(sentence[i])
            if actual != expected:
                return None  # Failed to validate checksum.
            return sentence

