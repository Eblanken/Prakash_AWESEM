from AWESEM_PiPion_Interface import AWESEM_PiPion_Interface
import numpy 

PiPion = AWESEM_PiPion_Interface()
PiPion.setVerbose(True)

# Standard test
print(PiPion.getDacFrequency(0))
print(PiPion.getDacFrequency(1))

PiPion.setDacFrequency(1, 12.00)
print(PiPion.getDacFrequency(1))

PiPion.setDacFrequency(0, 4.55)
print(PiPion.getDacFrequency(0))

PiPion.setDacMagnitude(0, 2.54)
print(PiPion.getDacMagnitude(0))

PiPion.setDacMagnitude(1, 1.24)
print(PiPion.getDacMagnitude(1))

PiPion.setDacWaveform(0, 0)
print(PiPion.getDacWaveform(0))
PiPion.setDacWaveform(1, 0)
print(PiPion.getDacWaveform(1))

print(PiPion.getAdcFrequency())
PiPion.setAdcFrequency(100.25)
print(PiPion.getAdcFrequency())

PiPion.beginEvents()

# Sets arbitrary waveform
# > Creates wavetable of lopsided triangle for testing
riseLength = 100
waveTable = numpy.round(numpy.concatenate((numpy.linspace(-32767, 32767, riseLength, endpoint = False), numpy.linspace(32767, -32767, 256 - riseLength, endpoint = False)))).astype(numpy.int16)
print(waveTable.shape)
print(len(waveTable))
# > Sets first
PiPion.pauseEvents()
print(PiPion.setCustomWaveformData(0, waveTable))
print(PiPion.setDacWaveform(0, 4))
print(PiPion.setDacMagnitude(0, 3.3))
PiPion.beginEvents()