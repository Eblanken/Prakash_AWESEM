% This script uses linear interpolation and spline interpolation to convert
% sensor data from a photodiode into displacement

sensorChannel = 1;
drivingChannel = 2;

experimentalSensorData = csvread('60.csv',6,0); % The data from the oscilloscope for the sensor
scaledVoltageReadings = csvread('Stage displacement vs photodiode voltage.csv',1,0); % The data from empirical measurement that maps voltage to displacement
scaledVoltageReadings(:,1) = (scaledVoltageReadings(:,1)./1000);

figure
hold on;
plot(experimentalSensorData(:,2));
hold off;

% Centers both data sets, also incidentally finds the amplitude etc. so
% this is mostly for graphing purposes
x = experimentalSensorData(:,1)';
y = experimentalSensorData(:,drivingChannel+1)';
%x = linspace(-0.1,0.1,100);
%yf = @(x) 2.5*sin(120*pi*x+2*pi*3);
%y = yf(x);
yu = max(y);
yl = min(y);
yr = (yu-yl);                            % Range of ?y?
yz = y-yu+(yr/2);
zx = x(yz .* circshift(yz,[0 1]) <= 0);     % Find zero-crossings
zz = zx(1);
per = 2*mean(diff(zx));                    % Estimate period
ym = mean(y);                              % Estimate offset
fit = @(b,x)  b(1).*(sin(2*pi*x./b(2) + 2*pi/b(3))) + b(4);    % Function to fit
fcn = @(b) sum((fit(b,x) - y).^2);                              % Least-Squares cost function
s = fminsearch(fcn, [yr;  per;  -0.0798;  ym]);                      % Minimise Least-Squares

%figure
%hold on;
%xp = experimentalSensorData(:,1);
%figure(1);
%plot(xp,fit(s,xp));
%plot(experimentalSensorData(:,1),experimentalSensorData(:,drivingChannel+1));
%legend('Sum Fit','The Real Data');
%legend('show');
%hold off;

% Converts the data
%outputDisplacementData = spline(scaledVoltageReadings(:,2),scaledVoltageReadings(:,1),experimentalSensorData(:,sensorChannel+1)); % This matrix stores the resulting displacements found for the readings
% Quick note, experimentalSensorData is of the form {point_1;point_2;point_3...}
% scaledVoltageReadings is of the form {voltage_1,displacement_1;voltage_2,displacement_2...}
% outputDisplacementData will be of the form {time_1,displacement_1;time_2,displacement_2...}
% so that it can be graphed and a curve fitted easily for later use.


%outputDisplacementData = [experimentalSensorData(:,1),outputDisplacementData(:,1)];

% Then we plot it
%figure;
%hold on;
%plot(outputDisplacementData(:,1),outputDisplacementData(:,2));
%title('Oscilloscope Sensor Data Converted to Displacement with Spline Interpolation');
%xlabel('Time');
%ylabel('Displacement');
%hold off;

% Plotting driving voltage
%figure;
%hold on;
%plot(experimentalSensorData(:,1),experimentalSensorData(:,drivingChannel+1));
%title('Forcing Voltage ');
%xlabel('Time');
%ylabel('Voltage');
%hold off;

% Plotting raw data
%figure;
%hold on;
%plot(experimentalSensorData(:,1),experimentalSensorData(:,sensorChannel+1));
%title('Time to Sensor Voltage ');
%xlabel('Time (s)');
%ylabel('Voltage (V)');
%hold off;

% Plotting scaling function
%figure;
%old on;
%plot(scaledVoltageReadings(:,1),scaledVoltageReadings(:,2));
%title('Sensor Displacement to Voltage ');
%xlabel('Displacement (mm)');
%ylabel('Voltage (V)');
%hold off;

function linearApproxValue = approx()

end