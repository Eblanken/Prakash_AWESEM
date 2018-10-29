#
# File: AWESEM_PiPion_Interface.py
# ------------------------------
# Author: Erick Blankenberg
# Date: 8/25/2018
#
# Description:
#   This class enables communication with the PiPion SEM
#   control system.
#   Transmission based off of:
#       https://folk.uio.no/jeanra/Microelectronics/TransmitStructArduinoPython.html
#   You could also use CmdMessenger but currently does not do structs. Getting
#   the data back may be difficult and/or inefficient.
#
# Note:
#   See the AWESEM_PiPion.ino file for command details and a comprehensive list.
#
# TODO:
#   - Connection validation and updating is bad, revisit this module

# ----------------------- Imported Libraries ------------------------------------

from   threading import Lock
import struct
import serial
import numpy
from serial.tools import list_ports


# ------------------------ Class Definition -------------------------------------

class AWESEM_PiPion_Interface:

    # Variables
    _verbose = True # Debugging
    _currentlyConnected = False
    _currentlyScanning  = False
    _serialPort = None # Object for serial communication
    _lastPacketID = 0 # How many sample packets have been recieved
    _guardLock    = Lock() # Had crashes when attempting to set parameters during reads

    # Constants
    _SERIAL_RECONNECTIONATTEMPTS = 1 # Number of times to try all ports once.
    _SERIAL_TIMEOUT = 0.1 # Timeout in seconds
    _SERIAL_DATASTRUCT_BUFFERSIZE = 1024 # Make sure that this is the same as specified in the MCU code

    # -------------------- Public Members ---------------

    # Initializes communications over serial to the PiPion
    def __init__(self):
        self.reconnectToPion()
        self._lastBlock = 0 # Tracks buffer count
        self.pauseEvents()  # Not trusting default state of PiPion

    # Safely closes the connection
    def __del__(self):
        self.pauseEvents()
        self.close()

    # Prints information for debugging
    def setVerbose(self, enableVerbose):
        self._verbose = enableVerbose

    def connectedToPion(self):
        return self._currentlyConnected

    # Attempts to reestablish connection with the PiPion
    def reconnectToPion(self):
        if self._findPort():
            self._currentlyConnected = True;
            return True
        return False

    # Safely closes the connection to the PiPion.
    def close(self):
        self._serialPort.close()

    def isScanning(self):
        return self._currentlyScanning

    #
    # Description:
    #   Pings the MCU to see if it is still alive.
    #
    # Returns:
    #   True if the MCU responds well, false otherwise.
    #
    def ping(self):
        self._sendBytes(b'p')
        return self._readBytes(1) == b'A'

    #
    # Description:
    #   Returns the DAC frequency of the given channel.
    #
    # Parameters:
    #   'dacChannel' The target channel, either 1 or 0.
    #
    # Returns:
    #   Floating point voltage.
    #
    def getDacFrequency(self, dacChannel):
        with self._guardLock:
            if self._currentlyConnected:
                self._sendBytes(struct.pack('<cb', b'f', dacChannel))
                if self._readBytes(1) == b'A':
                    return struct.unpack('<f', self._readBytes(4))
                elif self._verbose:
                    print("Error: AWSEM_getDacFrequency, ackowledgement failure")
            elif self._verbose:
                print("Error: AWSEM_getDacFrequency, unit disconnected")
            return None

    #
    # Description:
    #   Sets the waveform frequency of the given DAC dac channel
    #
    # Parameters:
    #   'dacChannel' The target channel, either 1 or 0.
    #
    # Returns:
    #   True if succesful, false otherwise.
    #
    # Note:
    #   Updated DAC channel frequency will not take effect until
    #   the beginEvents() and pauseEvents() commands are called.
    #
    def setDacFrequency(self, dacChannel, dacFrequency):
        with self._guardLock:
            if self._currentlyConnected:
                self._sendBytes(struct.pack('<cbf', b'F', dacChannel, dacFrequency))
                return self._readBytes(1) == b'A'
            return False

    #
    # Description:
    #   Returns the magnitude of the DAC waveform in volts.
    #
    # Parameters:
    #   'dacChannel' The target channel, either 1 or 0.
    #
    def getDacMagnitude(self, dacChannel):
        with self._guardLock:
            if self._currentlyConnected:
                self._sendBytes(struct.pack('<cb', b'm', dacChannel))
                if self._readBytes(1) == b'A':
                    return struct.unpack('<f', self._readBytes(4))
                elif self._verbose:
                    print("Error: AWSEM_getDacMagnitude, ackowledgement failure")
            elif self._verbose:
                print("Error: AWSEM_getDacMagnitude, unit disconnected")
            return None
    #
    # Description:
    #   Sets the magnitude of the DAC waveform in volts
    #   of the given channel.
    #
    # Parameters:
    #   'dacChannel'   The target channel, either 1 or 0.
    #   'dacMagnitude' The magnitude of the dac channel in volts.
    #                  Typically 3.3v max and centered at vref/2 (check MCU settings).
    #
    # Note:
    #   Updated DAC magnitude will not take effect until
    #   the beginEvents() and pauseEvents() commands are called.
    #
    def setDacMagnitude(self, dacChannel, dacMagnitude):
        with self._guardLock:
            if self._currentlyConnected:
                self._sendBytes(struct.pack('<cbf', b'M', dacChannel, dacMagnitude))
                return struct.unpack('<c', self._readBytes(1)) == b'A'
            return False

    #
    # Description:
    #   Returns the waveform assigned to the given dac channel.
    #
    # Parameters:
    #   'dacChannel' The target channel, either 1 or 0.
    #
    # Returns:
    #   The waveform associated with the channel
    #   0 = Sine, 1 = Sawtooth, 3 = Triangle.
    #
    def getDacWaveform(self, dacChannel):
        with self._guardLock:
            if self._currentlyConnected:
                self._sendBytes(struct.pack('<cb', b'w', dacChannel))
                if self._readBytes(1) == b'A':
                    return struct.unpack('<b', self._readBytes(1))
                elif self._verbose:
                    print("Error: AWSEM_getDacWaveform, ackowledgement failure")
            elif self._verbose:
                print("Error: AWSEM_getDacWaveform, unit disconnected")
            return None

    #
    # Description:
    #   Sets the waveform associated with the given dac channel.
    #
    # Parameters:
    #   'dacChannel'  The target channel, either 1 or 0.
    #   'dacWaveform' The waveform associated with the channel,
    #                 0 = Sine, 1 = Sawtooth, 3 = Triangle.
    #
    # Note:
    #   Updated DAC waveform settings will not take effect until
    #   the beginEvents() and pauseEvents() commands are called.
    #
    def setDacWaveform(self, dacChannel, dacWaveform):
        with self._guardLock:
            if self._currentlyConnected:
                self._sendBytes(struct.pack('<cbb', b'W', dacChannel, dacWaveform))
                return struct.unpack('<c', self._readBytes(1)) == b'A'
            return False

    #
    # Description:
    #   Returns the frequency in hertz that the ADC samples at.
    #
    # Returns:
    #   Returns the ADC frequency in hertz as a float.
    #
    def getAdcFrequency(self):
        with self._guardLock:
            if self._currentlyConnected:
                self._sendBytes(struct.pack('<c', b's'))
                return struct.unpack('<f', self._readBytes(4))
            return None

    #
    # Description:
    #   Sets the frequency of ADC sampling in hertz.
    #
    # Parameters:
    #   'adcFrequency' (float) The sampling frequency in hertz.
    #
    # Note:
    #   Updated ADC frequency will not take effect until
    #   the beginEvents() and pauseEvents() commands are called.
    #
    def setAdcFrequency(self, adcFrequency):
        with self._guardLock:
            if self._currentlyConnected:
                self._sendBytes(struct.pack('<cf', b'S', adcFrequency))
                return struct.unpack('<c', self._readBytes(1)) == b'A'
            return False

    #
    # Description:
    #   Sets the number of averaged samples per ADC result.
    #
    # Parameters:
    #   'adcAverages' The number of times to average per sample, must be 0, 4, 8, 16, or 32
    #
    # Returns:
    #   True if succesful, false otherwise.
    #
    # Note:
    #   Updated ADC frequency will not take effect until
    #   the beginEvents() and pauseEvents() commands are called.
    #
    def setAdcAverages(self, adcAverages):
        with self._guardLock:
            if self._currentlyConnected:
                self._sendBytes(struct.pack('<cb', b'U', adcAverages))
                return struct.unpack('<c', self._readBytes(1)) == b'A'
            return False

    #
    # Description:
    #   Returns the number of averages per ADC result, none
    #   if the device is disconnected.
    #
    # Returns:
    #   None if disconnected, integer number of averages per ADC result
    #   if connected.
    #
    def getAdcAverages(self):
        with self._guardLock:
            if self._currentlyConnected:
                self._sendBytes(struct.pack('<c', b'u'))
                return struct.unpack('<b')
            return None

    #
    # Description:
    #   Acquires a data buffer from the MCU.
    #
    # Returns:
    #   Returns an array of the form [dac 0 offset in uS, dac 1 offset in uS, byteValues]
    #
    def getDataBuffer(self):
        with self._guardLock:
            if self._currentlyConnected:
                self._sendBytes(struct.pack('<c', b'A'))
                ackResponse = self._readBytes(1)
                if ackResponse == b'A':
                    currentNumber = struct.unpack('<I', self._readBytes(4))
                    if(currentNumber[0] - self._lastPacketID - 1 > 0):
                        print("Error, AWESEM_getDataBuffer, missed %d packets", currentNumber[0] - self._lastPacketID - 1)
                    self._lastPacketID = currentNumber[0]
                    # Result consists of three 32 bit integers and then an
                    # array of bytes.
                    aOffset  = (struct.unpack('<I', self._readBytes(4)))[0]
                    bOffset  = (struct.unpack('<I', self._readBytes(4)))[0]
                    duration = (struct.unpack('<I', self._readBytes(4)))[0]
                    byteList = self._readBytes(self._SERIAL_DATASTRUCT_BUFFERSIZE)
                    byteArray = numpy.frombuffer(byteList, numpy.uint8)
                    value = numpy.stack((numpy.linspace(aOffset, aOffset + duration, self._SERIAL_DATASTRUCT_BUFFERSIZE), numpy.linspace(bOffset, bOffset + duration, self._SERIAL_DATASTRUCT_BUFFERSIZE), byteArray), 1) # format is [data, aTimes, bTimes] as column vectors
                    return value
                elif self._verbose:
                    print("Error: AWSEM_getDataBuffer, no buffer ready")
                    print(ackResponse)
            elif self._verbose:
                print("Error: AWSEM_getDataBuffer, unit disconnected")
            return None

    #
    # Description:
    #   Starts sampling and analog driving behavior.
    #
    def beginEvents(self):
        with self._guardLock:
            if self._currentlyConnected:
                outMessage = struct.pack('<c', b'B')
                self._sendBytes(outMessage)
                self._currentlyScanning = True
                return struct.unpack('<c', self._readBytes(1)) == b'A'
            return False
    #
    # Description:
    #   Ends sampling and analog driving behavior,
    #   also updates settings.
    #
    def pauseEvents(self):
        with self._guardLock:
            if self._currentlyConnected:
                outMessage = struct.pack('<c', b'H')
                self._sendBytes(outMessage)
                self._currentlyScanning = False
                return struct.unpack('<c', self._readBytes(1)) == b'A'
            return False

    #------------------- Private Members ---------------

    # Functions

    # Sends a serial command to the PiPion in the form of a byte array
    def _sendBytes(self, command):
        self._serialPort.write(command)

    # Reads values from the PiPion
    def _readBytes(self, numBytes):
        value = self._serialPort.read(numBytes)
        return value

    def _findPort(self):
        portList = list_ports.comports()
        if self._verbose:
            print("Searching for the PiPion:")
        for index in range(0, self._SERIAL_RECONNECTIONATTEMPTS):
            for currentPort in portList:
                try:
                    self._serialPort = serial.Serial(currentPort.device)
                    self._serialPort.close()
                    self._serialPort.open()
                    if self._verbose:
                        print(" Port: %s, %s, %s" % (currentPort.device, currentPort.name, currentPort.description))
                except:
                    continue
                self._serialPort.timeout = self._SERIAL_TIMEOUT
                if self.ping():
                    self._currentlyConnected = True
                    if self._verbose:
                        print('Connection established with the PiPion.')
                    return True
                else:
                    self._serialPort.close()
        if self._verbose:
            print('No serial ports found for the PiPion.')
        return False
