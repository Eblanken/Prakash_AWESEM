% This script is a test that I wrote to visualize the density of data points taken
% by a model AWESEM microscope as a function of distance from the center
% of the platfrom.

% Default header
clear all
clc
close all

% Function settings for the theoretical stage
platformSize = 1000;
traceWidth = 995;
%runTime = 30;
runTime = 10;
snapShotTime = 0.000001;

% Settings for the rotating stage
%slowFrequency_Rotate = 0.16667;
%fastFrequency_Rotate = 300;
slowFrequency_Rotate = 0.1;
fastFrequency_Rotate = 10;

% Settings for the double solenoid stage
%slowFrequency_Orthogonal = 0.1;
%fastFrequency_Orthogonal = 300;
slowFrequency_Orthogonal = 0.1;
fastFrequency_Orthogonal = 10;

% Settings for graphing
graphPoints = 500;

%---------------------- Rotating Stage Experiment ------------------------

testBed_Rotate = zeros(platformSize,platformSize);
x_Rotate = @(time) round(cos(2*pi*slowFrequency_Rotate*time)*(traceWidth/2)*sin(2*pi*fastFrequency_Rotate*time)+platformSize/2);
y_Rotate = @(time) round(sin(2*pi*slowFrequency_Rotate*time)*(traceWidth/2)*sin(2*pi*fastFrequency_Rotate*time)+platformSize/2);

% Sweeps the path across the test bed
for time = 0:snapShotTime:runTime
    testBed_Rotate(y_Rotate(time),x_Rotate(time)) = testBed_Rotate(y_Rotate(time),x_Rotate(time))+1;
end

% Catalogues scanned point frequency as a function of distance from the center
testBedData_Rotate = zeros(graphPoints,2);
maxRadius = (2*(platformSize/2)^2)^0.5;
testBedData_Rotate(:,1) = 0:(maxRadius)/(graphPoints-1):maxRadius;
for xIndex = 1:platformSize
    for yIndex = 1:platformSize
        radius = ((xIndex-(platformSize/2))^2+(yIndex-(platformSize/2))^2)^0.5;
        discreteRadius = floor(radius/((maxRadius)/(graphPoints-1))+1); % Extra 0.001 garuntees that the index wont be zero
        testBedData_Rotate(discreteRadius,2) = testBedData_Rotate(discreteRadius,2) + testBed_Rotate(yIndex,xIndex);
    end
end

% Plots the data
    % Plots the trajectory of the scanner
figure
pcolor(log(testBed_Rotate));
colorbar;
shading flat;
title('Trace of Scanned Points (Log)');
    % Plots the density of scanned points as a function of distance from the center
figure
yyaxis left;
plot(testBedData_Rotate(:,1),(testBedData_Rotate(:,2)./(testBedData_Rotate(:,1).*pi.*2)),'DisplayName','Density');
ylabel('Density (Points/Pixel)');
yyaxis right;
plot(testBedData_Rotate(:,1),testBedData_Rotate(:,2),'DisplayName','Quantity');
ylabel('Quantity');
xlim([0,traceWidth/2]);
title('Plot Density and Quantity Versus Distance From Origin');
xlabel('Distance (Pixels)');
legend('show');
    
%--------------------- Orthogonal Stage Experiment -----------------------

testBed_Orthogonal = zeros(platformSize,platformSize);
x_Orthogonal = @(time) round((traceWidth/2)*sin(2*pi*fastFrequency_Orthogonal*time)+platformSize/2);
y_Orthogonal = @(time) round((traceWidth/2)*sin(2*pi*slowFrequency_Orthogonal*time)+platformSize/2);

% Sweeps the path across the test bed
for time = 0:snapShotTime:runTime
    testBed_Orthogonal(y_Orthogonal(time),x_Orthogonal(time)) = testBed_Orthogonal(y_Orthogonal(time),x_Orthogonal(time))+1;
end

% Catalogues scanned point frequency as a function of distance from the center
testBedData_Orthogonal = zeros(graphPoints,2);
maxRadius = (2*(platformSize/2)^2)^0.5;
testBedData_Orthogonal(:,1) = 0:(maxRadius)/(graphPoints-1):maxRadius;
for xIndex = 1:platformSize
    for yIndex = 1:platformSize
        radius = ((xIndex-(platformSize/2))^2+(yIndex-(platformSize/2))^2)^0.5;
        discreteRadius = floor(radius/((maxRadius)/(graphPoints-1))+1); % Extra 0.001 garuntees that the index wont be zero
        testBedData_Orthogonal(discreteRadius,2) = testBedData_Orthogonal(discreteRadius,2) + testBed_Orthogonal(yIndex,xIndex);
    end
end

% Plots the data
    % Plots the trajectory of the scanner
figure
pcolor(log(testBed_Orthogonal));
colorbar;
shading flat;
title('Trace of Scanned Points (Log)');
    % Plots the density of scanned points as a function of distance from the center
figure
yyaxis left;
plot(testBedData_Orthogonal(:,1),(testBedData_Orthogonal(:,2)./(testBedData_Orthogonal(:,1).*pi.*2)),'DisplayName','Density');
ylabel('Density (Points/Pixel)');
yyaxis right;
plot(testBedData_Orthogonal(:,1),testBedData_Orthogonal(:,2),'DisplayName','Quantity');
ylabel('Quantity');
xlim([0,traceWidth/2]);
title('Plot Density and Quantity Versus Distance From Origin');
xlabel('Distance (Pixels)');
legend('show');
