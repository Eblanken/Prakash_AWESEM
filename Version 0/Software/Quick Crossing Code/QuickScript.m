% This script graphs data and a prediction

% Default header
clear all
clc
close all
 
% Function settings to approximate translation of stage
height = 176.5e-6; % Displacement from full positive extension to full negative extension of stage in meters <<<<<<<<<<< % Note: Roughly 57-64 line crossings per period depending on definition, used total crossings in one second divided by 20 travel sweeps per second multiplied by 12.5e-6 m per crossings, this is the total height of the wave, divide by two again to get the coefficient for the sine function
% ^ change this by at most 0.5 or 1, it is very close
frequency = 50; % Frequency in hertz
timeOffset = -0.00395+1/100; % Displacement function offset in seconds <<<<<<<<<
displacement = @(x) height*0.5*sin(frequency*2*pi*(x+timeOffset));

% Reads in the data
reading = csvread('50Hz.csv',9,0);
time = reading(:,1);
PDVolt = reading(:,2);
DVolt = reading(:,3);
 
% Graphs the photodiode voltage
figure
hold on;
ylabel('Photodiode Voltage (V)');
xlim([-0.5 -0.48]);
yyaxis left
plot(time,PDVolt);
legend('show');

% Plots theoretical sensor data
data = zeros(size(time));
for x = 1:size(time)
    data(x) = getGridValue(displacement(time(x)));
end
plot(time,data,'black')

% Plots the driving voltage
yyaxis right
plot(time,DVolt);
title('10 Hz 1D scan of Ronchi grid (10 um pitch)');
xlabel('Time (s)');
ylabel('Voice Coil Voltage (V)');
hold off;


% Identifies the number of times the threshold is crossed

% Limits the range for checking the number of crossing times
idxb = find(time == -0.5);
idxe = find(time == 0.5);
PDVolt_subset = PDVolt(1:size(time));

% Does iterations 
counter = 0;
for index = 2:size(PDVolt_subset)
    Threshold = 2.5;
    if ((PDVolt_subset(index)>=Threshold)&&(PDVolt_subset(index-1)<Threshold))
        counter = counter + 1;
    end
end

counter

% Returns intensity of beam at a given point
function a = getGridValue(x)
    % Data to approximate grid
    gridWireWidth = 5e-6; % How wide the wire is on the grid (m)
    gridGapWidth = 7.5e-6; % How big the gap is between wires (m)
    gridOffset = 0; % Shift of the grid in m <<<<<<<<<<<<<
    x = x + gridOffset;
    relativePositionToGridUnit = mod(x,(gridWireWidth+gridGapWidth));
    if relativePositionToGridUnit<gridWireWidth
        a = 1;
        return
    else
        a = 4;
        return
    end
end

