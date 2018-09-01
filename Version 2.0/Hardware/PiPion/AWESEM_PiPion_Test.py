from AWESEM_PiPion_Interface import AWESEM_PiPion_Interface
import serial
import time

PiPion = AWESEM_PiPion_Interface()

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