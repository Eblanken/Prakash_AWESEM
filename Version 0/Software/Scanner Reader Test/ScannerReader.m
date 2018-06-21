% This script is a simplification of the imaging analysis script

frequency = 73; % This is the frequency in hertz (1/s)
solenoidResponseOffset = 0.01; % This is how far the solenoid trails behind the voltage function (s)
vAmp = 1; % Aplitude of voltage response (not really important, never used for calculations) (v)
rAmp = 0.001; % Amplitude of solenoid response (m)

voltageFunction = @(t) vAmp*cos(2*pi*t*frequency); % This is the voltage function, used for reference only
responseFunction = @(t) (rAmp)+rAmp*cos(2*pi*(t+solenoidResponseOffset)*frequency); % This is the stage response function, same time reference as voltage

initialTime = 0; % (s)
finalTime = 0.025; % (s)
timeDivisions = 10000; % How many discrete points will be tested
maximumTimeScramble = 1000; % How many seconds the data can be displaced

gridWireWidth = 0.0001; % How wide the wire is on the grid (m)
gridGapWidth = 0.0001; % How big the gap is between wires (m)

% The actual program
timeDomain = linspace(initialTime,finalTime,timeDivisions);
acquiredIntensityData = zeros(timeDivisions,2); % Intensity paired with time (1) is t, (2) is intensity
acquiredVoltageData = zeros(timeDivisions,2); % Voltage paired with time (1) is t, (2) is intensity
pairedIntensityData = zeros(timeDivisions,2); % Intensity paired with displacement (1) is displacement, (2) is intensity


% gets the acquired data (Direct)
for index = 1:timeDivisions
    acquiredIntensityData(index,1) = timeDomain(index);
    acquiredIntensityData(index,2) = getGridValue(responseFunction(timeDomain(index)));
end

acquiredVoltageData(:,1) = timeDomain(:);
acquiredVoltageData(:,2) = voltageFunction(timeDomain(:));

% Plots the grid as it appears with time (Direct)
figure;
hold on;
plot(acquiredIntensityData(:,1),acquiredIntensityData(:,2));
title('Time versus Intensity (Sensor)(Direct Time)');
xlabel('Time (s)');
ylabel('Intensity');
hold off;

% Pairs the acquired data with its displacement (Direct)
pairedIntensityData(:,2) = acquiredIntensityData(:,2);
for index = 1:timeDivisions
    pairedIntensityData(index,1) = responseFunction(acquiredIntensityData(index,1));
end

% Plots the grid after the data points have been paired (Direct)
figure;
hold on;
plot(pairedIntensityData(:,1),pairedIntensityData(:,2));
title('Displacement versus Intensity (Sensor)(Direct Time)');
xlabel('Displacement (m)');
ylabel('Intensity');
hold off;


% Plots the grid as it appears in reality (Direct Time)
figure;
hold on;
genericRange = linspace(0,rAmp*2,1000);
genericValues = zeros(1000);
for index = 1:length(genericValues)
    genericValues(index) = getGridValue(genericRange(index));
end
plot(genericRange,genericValues);
title('Ideal Displacement versus Intensity (Ideal)');
xlabel('Displacement (m)');
ylabel('Intensity');
hold off;

% Acquires data when the time is initially scrambled
rng(0,'twister');
timeOffset = randi([-10 10],1,1);
for index = 1:length(acquiredVoltageData)
    acquiredVoltageData(index,1) = acquiredVoltageData(index,1)+timeOffset;
end

%------------------------- Data Analysis Program ------------------------%

% First we need to use the voltage function to get proper context for our
% solenoid movement function

% Identifies the coefficients for the voltage function A*cos(B*2*Pi*(x+C))+D
% We are really only interested in the C term, we already know the B term
% In later versions we may try to derive formulas for the solenoid movement
% on the fly but this is unlikely unless we have a strong model for the
% solenoids quality distribution.
% Parameter Vector Beta = [A,B,C,D]
betaInitial = [5,20,1,2];
size(betaInitial)
Beta = GaussNewtonCosineApprox(acquiredVoltageData(:,1),acquiredVoltageData(:,2),1200,1,betaInitial);
Beta

% For testing purposes plots the original function (with offset) and the
% approximation determined with the Guass algorithm.
figure;
hold on;
plot(acquiredVoltageData(:,1),acquiredVoltageData(:,2));
plot(acquiredVoltageData(:,1),Beta(1)*cos(Beta(2)*2*pi*(acquiredVoltageData(:,1)+Beta(3)))+Beta(4));
title('Time versus Voltage (Modded Time)');
xlabel('Displacement (m)');
ylabel('Intensity');
hold off;

% Returns intensity of beam at a given point
function a = getGridValue(x)
    gridWireWidth = 0.0001; % How wide the wire is on the grid (m)
    gridGapWidth = 0.0001; % How big the gap is between wires (m)
    relativePositionToGridUnit = mod(x,(gridWireWidth+gridGapWidth));
    if relativePositionToGridUnit<gridWireWidth
        a = 1;
        return
    else
        a = 0;
        return
    end
end

% Preforms the gauss newton algorithm to find the parameters for a sine fit
function Beta = GaussNewtonCosineApprox(dataX,dataY,iterations,alpha,Beta)
    r = zeros(length(dataY),1);
    J = zeros(length(dataY),length(Beta));
    for index = 1:iterations
        % Finds the r vector
        for yIndex = 1:length(dataY)
            r(yIndex,1) = dataY(yIndex) - GaussNewtonCosineFunction(dataX(yIndex),Beta,0);
        end
        % Finds the jacobean matrix J
        for paramIndex = 1:length(Beta)
            for xIndex = 1:length(dataX)
                J(xIndex,paramIndex) = GaussNewtonCosineFunction(dataX(xIndex),Beta,paramIndex);
            end
        end
        % Actually solves the equation
        delBeta = pinv(J)*r;%((transpose(J)*J)/transpose(J))*r;
        for betaIndex = 1:length(Beta)
            Beta(betaIndex) = Beta(betaIndex) + alpha*delBeta(betaIndex);
        end
    end
end

% Returns the value for the original cosine function (set derivativeTarget = 0) or a partial
% derivative with respect to the named derivativeTarget. If non-zero, the
% derivative target will use the partial derivative with respect to the
% parameter for a cosine of the form f(x,A,B,C) = A*cos(B*x+C)
function y = GaussNewtonCosineFunction(x,params,derivativeTarget)
    switch derivativeTarget
        case 0
            y = params(1)*cos(params(2)*2*pi*(x+params(3)))+params(4);
        case 1
            y = cos(params(2)*2*pi*(x+params(3)));
        case 2
            y = -2*pi*params(1)*sin(params(2)*2*pi*(x+params(3)));
        case 3
            y = -2*pi*params(1)*params(2)*sin(params(2)*2*pi*(x+params(3)));
        case 4
            y = 1;
    end   
end