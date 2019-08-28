# AWESEM Waveform Generation and Data Acquisition Front-End

--------------

## Description

This firmware acts as an analog front-end for the AWESEM program. The MCU both serves to generate the driving waveform for the sample stage with the on-board DAC and samples intensity data.

-----------
## Installation
This program is intended for the Teensy 3.6 board from PJRC. Make sure that you have Teensyduino installed. Open and compile the file "PiPion.ino" with the Arduino IDE.

------------
## Serial Commands

These are all of the commands that can be used with the MCU frontend. Note that all commands that set waveform and data acquisition parameters must be executed while the device is not running (after startup or after calling 'H' (halt)).

All command strings are of the format:

<a href="https://www.codecogs.com/eqnedit.php?latex=$\{\text{byte}_1,&space;\text{byte}_2,&space;[\text{byte}_3...\text{byte}_n&space;(\text{datatype}_1)],&space;[\text{byte}_{n&plus;1}&space;...\text{byte}_m&space;(\text{datatype}_2&space;)]\}$" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{byte}_1,&space;\text{byte}_2,&space;[\text{byte}_3...\text{byte}_n&space;(\text{datatype}_1)],&space;[\text{byte}_{n&plus;1}&space;...\text{byte}_m&space;(\text{datatype}_2&space;)]\}$" title="$\{\text{byte}_1, \text{byte}_2, [\text{byte}_3...\text{byte}_n (\text{datatype}_1)], [\text{byte}_{n+1} ...\text{byte}_m (\text{datatype}_2 )]\}$" /></a>

> __Ping__ <br>
> Call: <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'p'}\}$" title="$\{\text{'p'}\}$" /> <br>
> Response: <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'A'}\}$" title="$\{\text{'A'}\}$" />

> __Get frequency__ <br>
> Call: <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'f'},&space;[\text{axis&space;(uint8\_t)}]\}$" title="$\{\text{'f'}, [\text{axis (uint8\_t)}]\}$" /> <br>
> Response: If valid <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'A'}\}$" title="$\{\text{'A'}\}$" /> then <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{[\text{Frequency&space;Hz&space;(float)}]\}$" title="$\{[\text{Frequency Hz (float)}]\}$" />, otherwise <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'F'}\}$" title="$\{\text{'F'}\}$" />

> __Set Frequency__ <br>
> Call: <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'F'},&space;[text{channel&space;either&space;0&space;or&space;1&space;(uint8\_t)}],&space;[frequency&space;(float)]\}$" title="$\{\text{'F'}, [text{channel either 0 or 1 (uint8\_t)}], [frequency (float)]\}$" /> <br>
> Response: If valid <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{'A'\}$" title="$\{'A'\}$" /> otherwise <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{'F'\}$" title="$\{'F'\}$" />

> __Get VPP Range__ <br>
> Call: <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'m'},&space;[\text{axis&space;(uint8\_t)}]\}$" title="$\{\text{'m'}, [\text{axis (uint8\_t)}]\}$" /> <br>
> Response: If valid <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{'A'\}$" title="$\{'A'\}$" /> then <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{[\text{VPP&space;in&space;volts&space;(float)\}]\}}$" title="$\{[\text{VPP in volts (float)\}]\}}$" />, otherwise <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{'F'\}$" title="$\{'F'\}$" />.

> __Set VPP Range__ <br>
> Call: <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'M'},&space;[\text{axis&space;(uint8\_t)}],&space;[\text{magnitude&space;(float)}]\}$" title="$\{\text{'M'}, [\text{axis (uint8\_t)}], [\text{magnitude (float)}]\}$" />
<br>
> Response: If valid <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'A'}\}$" title="$\{\text{'A'}\}$" /> otherwise <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'F'}\}$" title="$\{\text{'F'}\}$" />

> __Get Sample Frequency__ <br>
> Call: <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'s'}\}$" title="$\{\text{'s'}\}$" /> <br>
> Response: If valid <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'A'}\}$" title="$\{\text{'A'}\}$" /> than <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{[\text{Sampling&space;Frequency&space;Hz&space;(float)}]\}$" title="$\{[\text{Sampling Frequency Hz (float)}]\}$" />, otherwise <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'F'}\}$" title="$\{\text{'F'}\}$" />.

> __Set Sample Frequency__ <br>
> Call: <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'S'},&space;[\text{frequency&space;(float)}]\}$" title="$\{\text{'S'}, [\text{frequency (float)}]\}$" /> <br>
> Response: If valid <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'A'}\}$" title="$\{\text{'A'}\}$" /> otherwise <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'F'}\}$" title="$\{\text{'F'}\}$" />

> __Get Sample Averages__ <br>
> : Call: <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\text{\{'u'\}}$" title="$\text{\{'u'\}}$" /> <br>
> : Response: If valid <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'A'}\}$" title="$\{\text{'A'}\}$" /> than <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{[\text{samples&space;averages&space;(uint8\_t)}]\}$" title="$\{[\text{samples averages (uint8\_t)}]\}$" />, otherwise <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'F'}\}$" title="$\{\text{'F'}\}$" />

> __Set Sample Averages__ <br>
> : Call: <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'U'},&space;[\text{averages&space;(uint8\_t)}]\}$" title="$\{\text{'U'}, [\text{averages (uint8\_t)}]\}$" /> <br>
> : Response: If valid <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'A'}\}$" title="$\{\text{'A'}\}$" /> otherwise <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'F'}\}$" title="$\{\text{'F'}\}$" />

> __Get Current Waveform__ <br>
> : Call: <img src="https://latex.codecogs.com/gif.latex?\inline&space;{'w',&space;[channel&space;0&space;or&space;1&space;(uint8_t)]}" title="{'w', [channel 0 or 1 (uint8_t)]}" /> <br>
> : Response: If valid <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{\text{'A'}\}$" title="$\{\text{'A'}\}$" /> than <img src="https://latex.codecogs.com/gif.latex?\inline&space;$\{[\text{0&space;=&space;Sine,&space;1&space;=&space;Sawtooth,&space;3&space;=&space;Triangle&space;(uint8\_t)}]\}$" title="$\{[\text{0 = Sine, 1 = Sawtooth, 3 = Triangle (uint8\_t)}]\}$" />, otherwise $\{\text{'F'}\}$

> Set Current Waveform
> : Call: $\{\text{'W'}, [\text{axis 0 or 1 (uint8\_t)}], [\text{waveform (0 sine, 1 saw, 3 tria, 4 arbitrary) (uint8\_t)}]\}$
> : Response: If valid $\{\text{'A'}\}$ otherwise $\{\text{'F'}\}$

> Set Arbitrary Waveform Data
> : Call: $\{\text{'D'}, [\text{axis 0 or 1 (uint8\_t)}], [\text{samples (int16\_t[256])}]\}$
> : Response: If valid $\{\text{'A'}\}$ otherwise $\{\text{'F'}\}$

> Request Buffer
> : Call: $\{\text{'A'}\}$
> : Response: If ready $\{\text{'A'}\}$ then $\{[\text{scan ID since start (uint8\_t)}], [\text{scan period uS (uint16\_t)}], [\text{time since last waveform rollover of 0 in uS (uint16\_t)}], [\text{rollover of 1 in uS (uint16\_t)}], [\text{data payload (uint8\_t[BUFFER\_SIZE])}]\}$

> Begin
> : Call: $\{\text{'B'}\}$
> : Response: If start is successful $\{\text{'A'}\}$ otherwise $\{\text{'F'}\}$

> Halt
> : Call: $\{\text{'H'}\}$
> : Response: If pause is successful $\{\text{'A'}\}$ otherwise $\{\text{'F'}\}$
