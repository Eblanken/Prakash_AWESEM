#
# File: AWESEM_PiPion_Interface.py
# ------------------------------
# Author: Erick Blankenberg
# Date: 8/25/2018
#
# Description:
#   This class enables communication with the PiPion SEM
#   control system.
#
#   Based off of:
#       https://folk.uio.no/jeanra/Microelectronics/TransmitStructArduinoPython.html
#
#   You could also use CmdMessenger but currently does not do structs.
#

# ----------------------- Imported Libraries ------------------------------------

import struct
import serial
from serial.tools import list_ports


# ------------------------ Class Definition -------------------------------------

class AWESEM_PiPion_Interface:

    # -------------------- Public Members ---------------

    # Initializes communications over serial to the PiPion
    def __init__(self):
        self.reconnectToPion()

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
        outMessage = struct.pack('cb', b'f', dacChannel)
        self._sendBytes(outMessage)
        buffer = self._readBytes(4);
        return struct.unpack('<f', buffer)

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
        outMessage = struct.pack('<cbf', b'F', dacChannel, dacFrequency)
        self._sendBytes(outMessage)
        response = self._readBytes(1);
        return response == b'A'

    #
    # Description:
    #   Returns the magnitude of the DAC waveform in volts.
    #
    # Parameters:
    #   'dacChannel' The target channel, either 1 or 0.
    #
    def getDacMagnitude(self, dacChannel):
        outMessage = struct.pack('<cb', b'm', dacChannel)
        self._sendBytes(outMessage)
        return struct.unpack('<f', self._readBytes(4))

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
        outMessage = struct.pack('<cbf', b'M', dacChannel, dacMagnitude)
        self._sendBytes(outMessage)
        result = (struct.unpack('<c', self._readBytes(1)) == b'A')
        
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
        outMessage = struct.pack('<cb', b'w', dacChannel)
        self._sendBytes(outMessage)
        return struct.unpack('<b', self._readBytes(1))
    
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
        outMessage = struct.pack('<cbb', b'W', dacChannel, dacWaveform)
        self._sendBytes(outMessage)
        result = (struct.unpack('<c', self._readBytes(1)) == b'A')
        
    #
    # Description:
    #   Returns the frequency in hertz that the ADC samples at.
    #
    # Returns:
    #   Returns the ADC frequency in hertz.
    #
    def getAdcFrequency(self):
        outMessage = struct.pack('<c', b's')
        self._sendBytes(outMessage)
        return struct.unpack('<f', self._readBytes(4))
    
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
        outMessage = struct.pack('<cf', b'S', adcFrequency)
        self._sendBytes(outMessage)
        result = (struct.unpack('<c', self._readBytes(1)) == b'A')

    #
    # Description:
    #   Acquires a data buffer from the MCU.
    #
    # Returns:
    #   Returns an array of the form [byte values, dac 0 offset in uS, dac 1 offset in uS]
    #
    def getDataBuffer(self):
        outMessage = struct.pack('<c', b'A')
        self._sendBytes(outMessage)
        # Result consists of two 32 bit integers and then an
        # array of bytes.
        byteArray = numpy.array(self._readBytes(self._DATASTRUCT_TIMEBYTES * 3 + self._DATASTRUCT_BUFFERSIZE))
        times = struct.unpack('<III', byteArray[0:8])
        duration = times(0)
        aOffset  = times(1)
        bOffset  = times(2)
        return numpy.concatenate(byteArray, numpy.linspace(aOffset, aOffset + duration, self._DATASTRUCT_BUFFERSIZE), numpy.linspace(bOffset, bOffset + duration, self._DATASTRUCT_BUFFERSIZE), 2) # format is [data, aTimes, bTimes] as column vectors

    #
    # Description:
    #   Starts sampling and analog driving behavior.
    #
    def beginEvents(self):
        outMessage = struct.pack('<c', b'B')
        self._sendBytes(outMessage)
        result = (struct.unpack('<c', self._readBytes(1)) == b'A')

    #
    # Description:
    #   Ends sampling and analog driving behavior,
    #   also updates settings.
    #
    def pauseEvents(self):
        outMessage = struct.pack('<c', b'H')
        self._sendBytes(outMessage)
        result = (struct.unpack('<c', self._readBytes(1)) == b'A')

    #------------------- Private Members ---------------

    # Functions

    # Sends a serial command to the PiPion in the form of a byte array
    def _sendBytes(self, command):
        self._serialPort.write(command)
        #if(self._verbose): TODO AWESEM_PiPion_Interface: console debug output
        #    print("Command is: %s" % command)

    # Reads values from the PiPion
    def _readBytes(self, numBytes):
        value = self._serialPort.read(numBytes)
        return value

    def _findPort(self):
        portList = list_ports.comports()
        if self._verbose:
            print("Searching for the PiPion:")
        for index in range(0, self._RECONNECTIONATTEMPTS):
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

    # Variables
    _verbose = True # Debugging
    _currentlyConnected = False
    _serialPort = None # Object for serial communication

    # Constants
    _SERIAL_RECONNECTIONATTEMPTS = 2 # Number of times to try all ports once.
    _SERIAL_TIMEOUT = 1 # Timeout in seconds
    _RECONNECTIONATTEMPTS = 5
    _DATASTRUCT_TIMEBYTES = 4 # Uses signed int
    _DATASTRUCT_BUFFERSIZE = 1024 # Make sure that this is the same as specified in the MCU code
