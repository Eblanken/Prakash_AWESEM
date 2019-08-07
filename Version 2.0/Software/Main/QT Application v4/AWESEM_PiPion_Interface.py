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
#   - b and a offsets where switched the whole time! Revisit what is defined as
#     a and b.
#   - Currently internal timing jumps around a bit which causes jumps. Probably rollover on the micros
#     used inside of the MCU. Should tie an interrupt to the audio output library
#     to handle the timing.

# ----------------------- Imported Libraries ------------------------------------

from   threading import Lock
import struct
import serial
import numpy
from serial.tools import list_ports


# ------------------------ Class Definition -------------------------------------

class AWESEM_PiPion_Interface:

    # Variables
    _verbose = False # Debugging
    _currentlyConnected = False
    _currentlyScanning  = False
    _serialPort = None # Object for serial communication
    _lastPacketID = 0 # How many sample packets have been recieved
    _guardLock    = Lock() # Had crashes when attempting to set parameters during reads

    # Current values

    _dacFrequencies = None
    _dacWaveforms   = None
    _dacMagnitudes  = None
    _adcFrequency   = None
    _adcAverages    = None

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
        # Updates client-side history to reflect default values in firmware
        self.getDacFrequency(1)
        self.getDacMagnitude(1)
        self.getDacWaveform(1)
        self.getAdcFrequency()
        self.getAdcAverages()

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

    def getBufferSize(self):
        return self._SERIAL_DATASTRUCT_BUFFERSIZE;

    #
    # Description:
    #   Returns the DAC frequency of the given channel.
    #
    # Parameters:
    #   'dacChannel'     The target channel, either 1 or 0.
    #   'forceDirect'    Asks from MCU rather than trust client-side record
    #
    # Returns:
    #   Floating point voltage.
    #
    def getDacFrequency(self, dacChannel, forceDirect = False):
        # Frequencies loaded in first time or if requested
        if self._dacFrequencies is None or forceDirect:
            with self._guardLock:
                if self._currentlyConnected:
                    if self._dacFrequencies is None:
                        self._dacFrequencies = dict()
                    for index in range(0, 2): # 0, 1
                        self._sendBytes(struct.pack('<cb', b'f', dacChannel))
                        response = self._readBytes(1)
                        if response == b'A':
                            self._dacFrequencies[index] = struct.unpack('<f', self._readBytes(4))
                        else:
                            if self._verbose:
                                print("Error: McuInterface_getDacFrequency, ackowledgement failure '%s'" % response.hex())
                            return None
                else:
                    if self._verbose:
                        print("Error: McuInterface_getDacFrequency, unit disconnected")
                    return None
        # Returns from prior history
        return self._dacFrequencies[dacChannel]

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
                response = self._readBytes(1)
                if response == b'A':
                    if self._dacFrequencies is None: # No history exists
                        self.getDacFrequency(0) # Forces loading of history from MCU
                    self._dacFrequencies[dacChannel] = dacFrequency
                    return True
                elif response == b'F':
                    if self._verbose:
                        print("Error, McuInterface_setDacFrequency, bad arguments")
                else:
                    if self._verbose:
                        print("Error: McuInterface_setDacFrequency, ackowledgement failure '%s'" % response.hex())
            else:
                if self._verbose:
                    print("Error: McuInterface_getDacFrequency, unit disconnected")
        return False

    #
    # Description:
    #   Returns the magnitude of the DAC waveform in volts.
    #
    # Parameters:
    #   'dacChannel'  The target channel, either 1 or 0.
    #   'forceDirect' True to request values from the MCU, false uses client-side history.
    #
    def getDacMagnitude(self, dacChannel, forceDirect = False):
        # Magnitudes loaded in first time or if requested
        if self._dacMagnitudes is None or forceDirect:
            with self._guardLock:
                if self._currentlyConnected:
                    if self._dacMagnitudes is None:
                        self._dacMagnitudes = dict()
                    for index in range(0, 2):
                        self._sendBytes(struct.pack('<cb', b'm', dacChannel))
                        response = self._readBytes(1)
                        if response == b'A':
                            self._dacMagnitudes[index] = struct.unpack('<f', self._readBytes(4))
                        else:
                            if self._verbose:
                                print("Error: McuInterface_getDacMagnitude, acknowledgement failure '%s'" % response.hex())
                            return None
                else:
                    if self._verbose:
                        print("Error: McuInterface_getDacMagnitude, unit disconnected")
                    return None
        return self._dacMagnitudes[dacChannel]
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
                response = self._readBytes(1)
                if response == b'A':
                    if self._dacMagnitudes is None: # No history exists
                        self.getDacMagnitude(0) # Forces loading of history from MCU
                    self._dacMagnitudes[dacChannel] = dacMagnitude
                    return True
                elif response == b'F':
                    if self._verbose:
                        print("Error, McuInterface_setDacMagnitude, bad arguments")
                else:
                    if self._verbose:
                        print("Error: McuInterface_setDacMagnitude, acknowledgement failure '%s'" % response.hex())
            else:
                if self._verbose:
                    print("Error: McuInterface_setDacMagnitude, unit disconnected")
        return False

    #
    # Description:
    #   Returns the waveform assigned to the given dac channel.
    #
    # Parameters:
    #   'dacChannel'  The target channel, either 1 or 0.
    #   'forceDirect' Load waveforms from the MCU rather than trust client-side history
    #
    # Returns:
    #   The waveform associated with the channel
    #   0 = Sine, 1 = Sawtooth, 3 = Triangle.
    #
    def getDacWaveform(self, dacChannel, forceDirect = False):
        # Magnitudes loaded in first time or if requested
        if self._dacWaveforms is None or forceDirect:
            with self._guardLock:
                if self._currentlyConnected:
                    if self._dacWaveforms is None: # No prior history
                        self._dacWaveforms = dict() # Creates history structure
                    for index in range(0, 2): # 0, 1
                        self._sendBytes(struct.pack('<cb', b'w', dacChannel))
                        response = self._readBytes(1)
                        if response == b'A':
                            self._dacWaveforms[index] = struct.unpack('<b', self._readBytes(1))
                        else:
                            if self._verbose:
                                print("Error: McuInterface_getDacWaveform, ackowledgement failure '%s'" % response.hex())
                            return None
                else:
                    if self._verbose:
                        print("Error: McuInterface_getDacWaveform, unit disconnected")
                    return None
        return self._dacWaveforms[dacChannel]

    #
    # Description:
    #   Sets the waveform associated with the given dac channel.
    #
    # Parameters:
    #   'dacChannel'  The target channel, either 1 or 0.
    #   'dacWaveform' The waveform associated with the channel,
    #                 0 = Sine, 1 = Sawtooth, 3 = Triangle, 4 = Custom
    #
    # Note:
    #   Updated DAC waveform settings will not take effect until
    #   the beginEvents() and pauseEvents() commands are called.
    #
    def setDacWaveform(self, dacChannel, dacWaveform):
        with self._guardLock:
            if self._currentlyConnected:
                self._sendBytes(struct.pack('<cbb', b'W', dacChannel, dacWaveform))
                response = self._readBytes(1)
                if response == b'A':
                    if self._dacWaveforms is None: # No client-side history
                        self.getDacWaveform(0) # Creates client-side history structure
                    self._dacWaveforms[dacChannel] = dacWaveform
                    return True
                elif response == b'F':
                    if self._verbose:
                        print("Error: McuInterface_setDacWaveform, bad arguments")
                else:
                    if self._verbose:
                        print("Error: McuInterface_setDacWaveform, ackowledgement failure '%s'" % response.hex())
            else:
                if self._verbose:
                    print("Error: McuInterface_setDacWaveform, unit disconnected")
        return False

    #
    # Description:
    #   Sets custom waveform information for the given channel
    #
    # Parameters:
    #   'dacChannel'    The target channel, either 1 or 0.
    #   'waveformArray' The 256 value 16 bit integer LUT that the MCU should use (is linearily interpolated)
    #
    # Note:
    #   Updated DAC waveform settings will not take effect until
    #   the beginEvents() and pauseEvents() commands are called.
    #
    def setCustomWaveformData(self, dacChannel, waveformArray):
        if(waveformArray.shape[0] != 256):
            print("Error: MCUInterface_setCustomWaveformData, waveform wrong shape")
            return False
        if(numpy.sum(numpy.logical_or(waveformArray > 32767, waveformArray < -32767))):
            print("Error: MCUInterface_setCustomWaveformData, waveform values out of range")
            return False
        waveformArray = waveformArray.astype(np.int16)
        # Loads values into MCU
        with self._guardLock:
            if self._currentlyConnected:
                self._sendBytes(struct.pack('<c256h', b'D', adcAverages, *array(waveformArray)))
                response = self._readBytes(1)
                if response == b'A':
                    return True
                else:
                    if self._verbose:
                        print("Error: MCUInterface_setCustomWaveformData, acknowledgement failure '%s'" % response.hex())
                    return None
            else:
                if self._verbose:
                    print("Error: MCUInterface_setCustomWaveformData, unit disconnected")
                return None


    #
    # Description:
    #   Returns the frequency in hertz that the ADC samples at.
    #
    # Parameters:
    #   'forceDirect' If true, reloads record from MCU rather than use client-side history
    #
    # Returns:
    #   Returns the ADC frequency in hertz as a float.
    #
    def getAdcFrequency(self, forceDirect = False):
        if self._adcFrequency is None or forceDirect:
            with self._guardLock:
                if self._currentlyConnected:
                    self._sendBytes(struct.pack('<c', b's'))
                    response = self._readBytes(1)
                    if response == b'A':
                        self._adcFrequency = struct.unpack('<f', self._readBytes(4))
                    else:
                        if self._verbose:
                            print("Error: McuInterface_getAdcFrequency, acknowledgement failure '%s'" % response.hex())
                        return None
                else:
                    if self._verbose:
                        print("Error: McuInterface_getAdcFrequency, unit disconnected")
                    return None
        return self._adcFrequency

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
                response = self._readBytes(1)
                if response == b'A':
                    self._adcFrequency = adcFrequency
                    return True
                elif response == b'F':
                    if self._verbose:
                        print("Error: McuInterface_setAdcFrequency, bad arguments")
                else:
                    if self._verbose:
                        print("Error: McuInterface_setAdcFrequency, acknowledgement failure  '%s'" % response.hex())
            else:
                if self._verbose:
                    print("Error: McuInterface_setAdcFrequency, unit disconnected")
        return False

    #
    # Description:
    #   Returns the number of averages per ADC result, none
    #   if the device is disconnected.
    #
    # Parameters:
    #   'forceDirect' If true, reloads record from MCU rather than use client-side history
    #
    # Returns:
    #   None if disconnected, integer number of averages per ADC result
    #   if connected.
    #
    def getAdcAverages(self, forceDirect = False):
        if self._adcAverages is None or forceDirect:
            with self._guardLock:
                if self._currentlyConnected:
                    self._sendBytes(struct.pack('<c', b'u'))
                    response = self._readBytes(1)
                    if response == b'A':
                        self._adcAverages = struct.unpack('<b', self._readBytes(1))
                    else:
                        if self._verbose:
                            print("Error: McuInterface_getAdcAverages, ackowledgement failure '%s'" % response.hex())
                else:
                    if self._verbose:
                        print("Error: McuInterface_getAdcAverages, unit disconnected")
        return self._adcAverages

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
                response = self._readBytes(1)
                if response == b'A':
                    self._adcAverages = adcAverages
                    return True
                elif response == b'F':
                    if self._verbose:
                        print("Error: McuInterface_setAdcAverages, bad arguments")
                else:
                    if self._verbose:
                        print("Error: McuInterface_setAdcAverages, ackowledgement failure '%s'" % response.hex())
            else:
                if self._verbose:
                    print("Error: McuInterface_setAdcAverages, unit disconnected")
        return False

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
                response = self._readBytes(1)
                if response == b'A':
                    currentNumber = struct.unpack('<I', self._readBytes(4))
                    if(currentNumber[0] - self._lastPacketID - 1 > 0):
                        print("Error, McuInterface_getDataBuffer, missed %d packets" % (currentNumber[0] - self._lastPacketID - 1))
                    self._lastPacketID = currentNumber[0]
                    # Result consists of three 32 bit integers and then an
                    # array of bytes.
                    aOffset  = (struct.unpack('<I', self._readBytes(4)))[0] # In microseconds
                    bOffset  = (struct.unpack('<I', self._readBytes(4)))[0] # In microseconds
                    print(aOffset)
                    print(bOffset)
                    duration = (struct.unpack('<I', self._readBytes(4)))[0]
                    byteList = self._readBytes(self._SERIAL_DATASTRUCT_BUFFERSIZE)
                    byteArray = numpy.frombuffer(byteList, numpy.uint8)
                    value = numpy.stack((numpy.linspace(bOffset, bOffset + duration, self._SERIAL_DATASTRUCT_BUFFERSIZE) / 1000000.0, numpy.linspace(aOffset, aOffset + duration, self._SERIAL_DATASTRUCT_BUFFERSIZE) / 1000000.0, byteArray), 1) # format is [data, aTimes, bTimes] as column vectors
                    return value
                #elif response == b'F':
                    #if self._verbose:
                        #print("Error: AWSEM_getDataBuffer, no buffer ready")
                    #return None
                else:
                    if self._verbose:
                        print("Error: McuInterface_getDataBuffer, ackowledgement failure '%s'" % response.hex())
                    return None
            else:
                if self._verbose:
                    print("Error: McuInterface_getDataBuffer, unit disconnected")
                return None
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
                response = self._readBytes(1)
                if response == b'A':
                    self._currentlyScanning = True
                    return True
                else:
                    if self._verbose:
                        print("Error, McuInterface_beginEvents, ackowledgement failure '%s'" % response.hex())
            else:
                if self._verbose:
                    print("Error, McuInterface_beginEvents, unit disconnected")
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
                response = self._readBytes(1)
                if response == b'A':
                    return True
                else:
                    if self._verbose:
                        print("Error, McuInterface_beginEvents, ackowledgement failure")
                    return False
            else:
                if self._verbose:
                    print("Error, McuInterface_pauseEvents, unit disconnected")
                return False
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
            print("McuInterface, Searching for the PiPion:")
        for index in range(0, self._SERIAL_RECONNECTIONATTEMPTS):
            for currentPort in portList:
                try:
                    self._serialPort = serial.Serial(currentPort.device)
                    self._serialPort.close()
                    self._serialPort.open()
                    if self._verbose:
                        print("  -> Port: %s, %s, %s" % (currentPort.device, currentPort.name, currentPort.description))
                except:
                    continue
                self._serialPort.timeout = self._SERIAL_TIMEOUT
                if self.ping():
                    self._currentlyConnected = True
                    if self._verbose:
                        print('McuInterface, Connection established with the PiPion.')
                    return True
                else:
                    self._serialPort.close()
        if self._verbose:
            print('McuInterface, No serial ports found for the PiPion.')
        return False
