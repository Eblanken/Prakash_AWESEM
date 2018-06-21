%2D Scan Image Processing
 
close all
clc
clear all
 
T_fast = 50;
T_slow = 0.05;
V_amp_slow = 0.5;
 
data = csvread('50Hz_50mHz_300mV_reference.csv',9,0); % 9, 0
time = data(:,1) + max(data(:,1)); % makes time start from 0, assumes time is -t to +t
V_Photodiode = data(:,2);
% V_Slow = data(:,3);
% max(data(:,2))
% min(data(:,2))

matrixDivisions = 150;

%--------------------------- Reconstructs Image from Movement -------------

sDisp = 1; %20*(7.5+5.0)*10^-6; % Total travel distance in meters % Only relevant for scaling
fDisp = 1; %20*(7.5+5.0)*10^-6; % Total travel distance in meters
%slowSolenoidResponseOffset = (1/T_slow)*(0.100); % Response offset in seconds, decimal fraction of period
%fastSolenoidResponseOffset = (1/T_fast)*(0.8855); % Response offset in seconds, decimal fraction of period

slowSolenoidResponseOffset = (1/T_slow)*(0.08); % Response offset in seconds, decimal fraction of period
fastSolenoidResponseOffset = (1/T_fast)*(0.885);

index = 1;
space = linspace(-1,0,((2 * T_fast) + 1) / 4);

averagingVector = zeros(1,length(space));
for arbValue = space
    start = find((data(:,1) > arbValue),1);
    finish = find((data(:,1) > arbValue + 1/T_fast),1);
    averagingVector(index) = getOffsetApproximation(data(start:finish,2));
    index = index + 1;
end
sum(averagingVector) / numel(averagingVector);
averagingVector;
plot(averagingVector);

slowSinePosition = @(t) sDisp*0.5*sin(2*pi*T_slow*(t+slowSolenoidResponseOffset));
%fastSinePosition = @(t) fDisp*0.5*sin(2*pi*T_fast*(t+fastSolenoidResponseOffset));

% coordinate paired data is of the form X,Y,Intensity
coordinatePairedData = zeros(length(time),4);

% Assigns X and Y coordinates to data based on time
for index = 1:length(coordinatePairedData)
    coordinatePairedData(index,1) = slowSinePosition(time(index));
    coordinatePairedData(index,2) = sine(time(index),fDisp,T_fast,fastSolenoidResponseOffset);%fastSinePosition(time(index));
    coordinatePairedData(index,3) = V_Photodiode(index);
    coordinatePairedData(index,4) = time(index);
end
%plot(coordinatePairedData(150000:650000,1));
coordinatePairedData = coordinatePairedData(150000:650000,:);

% Builds array that can be plotted
imageDimension = max([sDisp,fDisp]);
matrixDigitalUnit = imageDimension/(matrixDivisions-1);
coordinatePairedData(:,1) = floor((coordinatePairedData(:,1)+imageDimension/2)/matrixDigitalUnit)+1;
coordinatePairedData(:,2) = floor((coordinatePairedData(:,2)+imageDimension/2)/matrixDigitalUnit)+1;

dataArray = zeros(matrixDivisions+1,matrixDivisions+1);
indexArray = zeros(matrixDivisions+1,matrixDivisions+1);

for index = 1:length(coordinatePairedData)
    x = coordinatePairedData(index,1);
    y = coordinatePairedData(index,2);
    dataArray(x,y) = dataArray(x,y) + coordinatePairedData(index,3);
    indexArray(x,y) = indexArray(x,y) + 1;
end
indexArray(indexArray == 0) = 1;
dataArray = dataArray./indexArray;

% Graphs reconstructed data
figure;
pcolor(dataArray);
colormap(gray);
title(['(RECONSTRUCTED) 2D Scan: ' num2str(T_slow) ' Hz @ ' num2str(V_amp_slow) 'V, ' num2str(T_fast) ' Hz, ' num2str(coordinatePairedData(length(coordinatePairedData),4)-coordinatePairedData(1,4)) ' secs long'])
shading flat;

%{
% Graphs how frequently data piled up for reference
figure
pcolor(log(indexArray));
shading flat;
title('Logarithmic Data Density');
%}

% -------> Further Processes Reconstructed Data

thresholdImage = thresholdFilter(dataArray, sum(sum(dataArray)) / numel(dataArray));
figure;
pcolor(thresholdImage);
colormap(gray);
title('Threshold Applied');
shading flat;

%{
blobImage = blobIdentification(thresholdImage);
figure;
pcolor(blobImage);
title('Blobs Identified');
shading flat;
%}

trimmedBlobImage = killEdgeBlobs(thresholdImage, 2);
blobStatistics = blobCatalog(trimmedBlobImage);

% Processes blobStatistics
neighborStatistics = neighborCatalog(blobStatistics, 4);
figure;
histogram(neighborStatistics(:, 3), 35);
title('Distribution of Magnitudes of Distance Between Grid Points (Pixels)');
% Sorts stats into bins % TODO replace with actual curve fitting + analysis
maxDistanceValue = max(neighborStatistics(:, 3));
numDistanceDivisions = 20;
distanceBins = zeros(1, numDistanceDivisions);
for index = 1:length(neighborStatistics)
    value = ceil(neighborStatistics(index, 3) * (numDistanceDivisions / maxDistanceValue));
    distanceBins(value) = distanceBins(value) + 1;
end
[maxDistanceBinCount, maxDistanceBinNumber] = max(distanceBins);
maxDistanceFromBin = maxDistanceBinNumber * (maxDistanceValue / numDistanceDivisions);

figure
histogram(neighborStatistics(:, 4).*(360 / (2*pi)), 35);
title('Distribution of Co-angles Between Points (Degrees)');
% Sorts stats into bins % TODO find slant from angle discrepency
numAngleDivisions = 50;
angleBins = zeros(1, numAngleDivisions);
for index = 1:length(neighborStatistics)
    value = floor((neighborStatistics(index, 4) + pi / 2) * (numAngleDivisions / pi)) + 1; % Functionally angle only ranges from - Pi / 2 to Pi / 2
    angleBins(value) = angleBins(value) + 1;
end
[maxAngleBinCount, maxAngleBinNumber] = max(angleBins);
maxAngleFromBin = maxAngleBinNumber * (pi / numAngleDivisions) - pi / 2;

% Plots blobs and reconstructed grid
figure
hold on;
pcolor(trimmedBlobImage);
title('Blobs Identified, Edge Blobs Removed');
shading flat;
blobCentroidScatter = scatter(blobStatistics(:,4), blobStatistics(:,3), blobStatistics(:,1));
blobCentroidScatter.LineWidth = 0.6;
blobCentroidScatter.MarkerEdgeColor = [1 0 0];
blobCentroidScatter.MarkerFaceColor = [1 0 0];

% Attempts to match a grid to the selected coordinates
% Creates grid
statsSize = size(blobStatistics);
numPoints = statsSize(1);
newPointVolume = 100;
edgeNumPoints = 10;

% Original grid points all have a distance of 1 and no initial angle
% Builds original grid
modelXComponents = 1:edgeNumPoints;
modelYComponents = 1:edgeNumPoints;
modelX = zeros(1, newPointVolume);
modelY = zeros(1, newPointVolume);
for rowIndex = 1:length(modelYComponents)
    for colIndex = 1:length(modelXComponents)
        modelX((rowIndex - 1) * edgeNumPoints + colIndex) = modelXComponents(colIndex);
        modelY((rowIndex - 1) * edgeNumPoints + colIndex) = modelYComponents(rowIndex);
    end
end
model = [modelX; modelY];
% Generates initial rotation and scaling transform from distributions
rotationVector = [cos(-maxAngleFromBin), sin(-maxAngleFromBin); -sin(-maxAngleFromBin), cos(-maxAngleFromBin)];
scaleVector = [maxDistanceFromBin, 0; 0, maxDistanceFromBin];

compositeVector = scaleVector * rotationVector;

size(compositeVector)
size(model(:, 1))
size(compositeVector * model(:, 1))

% Applies transformation vector
for index = 1:length(model)
    model(:, index) = compositeVector * model(:, index);
end

data = [blobStatistics(:,4)'; blobStatistics(:,3)'];

[TR,TT,newData] = icp(data, model, 500, 100);
matchedGridScatter = scatter(newData(1,:), newData(2,:), ones(1, length(newData)));
matchedGridScatter.LineWidth = 5;
matchedGridScatter.MarkerEdgeColor = [1 0 0.5];
matchedGridScatter.MarkerFaceColor = [1 0 0.5];
modelScatter = scatter(model(1,:), model(2,:), ones(1, length(model)));
modelScatter.LineWidth = 5;
modelScatter.MarkerEdgeColor = [(50 / 255), (205 / 255), (50 / 255)];
modelScatter.MarkerFaceColor = [(50 / 255), (205 / 255), (50 / 255)];
hold off

%{
boundaryImage = simpleEdgeFilter(trimmedBlobImage);
figure;
pcolor(boundaryImage);
colormap(gray);
title('Boundaries');
shading flat;

houghGraph = houghTransform(boundaryImage, 180);
figure;
pcolor(houghGraph);
title('Hough Graph of Image');
shading flat;

boxBlurKernel = [1, 1, 1 ; 1, 1, 1 ; 1, 1, 1];
boxBlurred = convolveFilter(dataArray, boxBlurKernel);
figure;
pcolor(boxBlurred);
colormap(gray);
title('Convolved with Box Blur');
shading flat;

erodedImage = erodeFilter(thresholdImage, 3, 1);
figure;
pcolor(erodedImage);
colormap(gray);
title('Eroded with Mask of Size 5');
shading flat;

%}

%---------------- Graphs Stacking of Periods For Reference ----------------

% Builds array for simple graphing, stacks fast periods
PD_Volt = V_Photodiode'; %transposes the PDVoltage array so that it's a row rather than a column vector
numberOfLines = T_fast/T_slow;
numberOfLines;
length(PD_Volt);
length(PD_Volt)/numberOfLines;
PD_Volt_2D = reshape(PD_Volt,length(PD_Volt)/numberOfLines,numberOfLines);

figure;
pcolor(PD_Volt_2D');
colormap(gray);
shading flat;
title(['(BASIC) 2D Scan: ' num2str(T_slow) ' Hz @ ' num2str(V_amp_slow) 'V, ' num2str(T_fast) ' Hz, ' num2str(max(time)) ' secs long'])
ylabel('Scan Line Number');

%----------------------- Function Definitions -----------------------------

%
% This function just returns a vector that contains a list of point
% pairings, the magnitude of the vector between the points, the angle
% of this vector, and the components of the vector. The function returns a
% matrix of the form [[ID1, ID2, Magnitude, CoAngle, DRow, DColumn] ; ... ]
%
% The function takes in a matrix of the form provided by blobStatistics
% and an integer 'numNeighbors' which limits the number of closest neighbors
% recorded
%
% TODO replace with more efficient structures so that the runtime is better
% than N^2.
%
function neighborStatistics = neighborCatalog(blobStatistics, numNeighbors) 
    % Blob statistics is of the form [ID, size, column (x), row (y)

    % The function
    statisticsSize = size(blobStatistics);
    neighborStatistics = zeros(statisticsSize(1) * numNeighbors, 6);
    % For each point, finds closest neighbors
    % All edges are cataloged twice, once for each involved point
    for targetIndex = 1:statisticsSize(1)
        % TODO re-implement as a real priority queue or other structure.
        for neighborIndex = 1:statisticsSize(1)
            % For each valid neighbor, trickles the new neighbor down the
            % existing list as far as possible so that the list is ordered.
            if targetIndex ~= neighborIndex
                % Builds profile of current possible link
                dRow = blobStatistics(neighborIndex, 3) - blobStatistics(targetIndex, 3);
                dColumn = blobStatistics(neighborIndex, 4) - blobStatistics(targetIndex, 4);
                magnitude = (dRow^2 + dColumn^2)^0.5;
                coAngle = atan(dRow / dColumn);
                targetNeighborEntry = [blobStatistics(targetIndex,1), blobStatistics(neighborIndex,1), magnitude, coAngle, dRow, dColumn];
                % Attempts to load profile into the dataset
                for replaceIndex = ((targetIndex - 1) * numNeighbors) + 1:(targetIndex * numNeighbors) % Iterates from last to first
                    % If next highest neighbor is closer, do nothing.
                    % Otherwise displace the next highest neighbor.
                    if (targetNeighborEntry(3) > neighborStatistics(replaceIndex, 3)) && (neighborStatistics(replaceIndex, 1) ~= 0)
                        break;
                    else
                        currentValue = neighborStatistics(replaceIndex, :);
                        neighborStatistics(replaceIndex, :) = targetNeighborEntry;
                        % Repositions displaced entry only if
                        % the displaced entry is not already at the bottom
                        if replaceIndex > ((targetIndex - 1) * numNeighbors) + 1
                            neighborStatistics(replaceIndex - 1, :) = currentValue;
                        end
                    end
                end
            end
        end
    end
end

%
% This function finds the centroid of all distinctly numbered
% blobs in the image greater than 0. 
%
% It is assumed that the imageMatrix is a binary image where the
% background has a value of zero and all non zero cells have values
% that link them to a single blob id.
%
% The statistics for each blob are cataloged in a row, the first
% entry in the row is the id of the blob, the second entry is the surface
% area of the blob, the third and fourth entries are the x and y
% coordinates of the centroid of the shape.
%
function blobStatistics = blobCatalog(imageMatrix)
    blobStatistics = [];
    imageDimensions = size(imageMatrix);
    for rowIndex = 1:imageDimensions(1)
        for columnIndex = 1:imageDimensions(2)
            value = imageMatrix(rowIndex, columnIndex);
            % We only care about foreground pixels
            if value ~= 0    
                % If the current pixel value has not already been cataloged, we
                % create a new entry in blobStatistics to capture it
                if (isempty(blobStatistics) || ~(ismember(value, blobStatistics(:,1))))
                    newRow = [value, 0, 0, 0];
                    blobStatistics = [blobStatistics; newRow];
                end
                currentRowIndex = find(blobStatistics(:,1) == value);

                % Surface area is simple
                blobStatistics(currentRowIndex, 2) = blobStatistics(currentRowIndex, 2) + 1;

                % During cataloging, x and y coordinates are repositories for
                % the accumulator that is later divided by area
                blobStatistics(currentRowIndex, 3) = blobStatistics(currentRowIndex, 3) + rowIndex;
                blobStatistics(currentRowIndex, 4) = blobStatistics(currentRowIndex, 4) + columnIndex;
            end
        end
    end

    blobStatistics(:,3) = blobStatistics(:,3)./blobStatistics(:,2);
    blobStatistics(:,4) = blobStatistics(:,4)./blobStatistics(:,2); % Equivalent to sum[value * index / value]
end

%
% This function erodes the given image so that the area occupied by
% the value specified by targetValue increases. This function can be
% adopted for dialation if the foreground value is specified.
%
function erodedImage = erodeFilter(imageMatrix, maskSize, targetValue)
    imageDimensions = size(imageMatrix);
    erodedImage = imageMatrix;
    % Acts on each pixel
    for rowIndex = 1:imageDimensions(1)
        for columnIndex = 1:imageDimensions(2)
            if imageMatrix(rowIndex, columnIndex) ~= targetValue
                % If any neighbors within the mask are of targetValue, the
                % target pixel becomes targetValue
                for rowCheck = floor(-maskSize / 2):ceil(maskSize / 2)
                    for columnCheck = floor(-maskSize / 2):ceil(maskSize / 2)
                        currentRow = rowCheck + rowIndex;
                        currentColumn = columnCheck + columnIndex;
                        if (min(currentRow, imageDimensions(1)) == max(currentRow, 1)) && (min(currentColumn, imageDimensions(2)) == max(currentColumn, 1))
                            if imageMatrix(currentRow, currentColumn) == targetValue
                                erodedImage(rowIndex, columnIndex) = targetValue;
                                break; % // TODO incomplete breaking
                            end
                        end
                    end
                end
            end
        end
    end
end

%
% This function convolves the given imageMatrix with the given convolution
% kernel.
%
% This function assumes that the values along the edges extend infinitely
% normal to the edge.
%
function convolvedImage = convolveFilter(imageMatrix, convolveKernel)
    kernelTotal = sum(sum(convolveKernel));
    imageDimensions = size(imageMatrix);
    kernelDimensions = size(convolveKernel);
    convolvedImage = zeros(imageDimensions);
    
    % Operates on each pixel
    for rowIndex = 1:imageDimensions(1)
        for columnIndex = 1:imageDimensions(2)
            accumulator = 0;
            % Preforms convolution operation
            for kernelRow = 1:kernelDimensions(1)
                for kernelColumn = 1:kernelDimensions(2)
                    currentRow = rowIndex + floor(kernelDimensions(1) / 2 - (kernelRow - 1));
                    currentColumn = columnIndex + floor(kernelDimensions(2) / 2 - (kernelColumn - 1));
                    
                    % Applies boundary checking
                    if currentRow < 1
                        currentRow = 1;
                    elseif currentRow > imageDimensions(1)
                        currentRow = imageDimensions(1);
                    end
                    
                    if currentColumn < 1
                        currentColumn = 1;
                    elseif currentColumn > imageDimensions(2)
                        currentColumn = imageDimensions(2);
                    end
                    
                    % Kernel operation is the sum of the image values
                    % around a target multiplied by the corresponding
                    % values in the kernel (inverted)
                    imageMatrix(currentRow, currentColumn) * convolveKernel(kernelRow, kernelColumn);
                    accumulator = accumulator + imageMatrix(currentRow, currentColumn) * convolveKernel(kernelRow, kernelColumn);
                end
            end
            convolvedImage(rowIndex, columnIndex) = (accumulator / kernelTotal);
        end
    end
end

%
% This function just returns an image matrix where any values
% above the value parameter in the original image are marked
% as 1 and any values below that threshold are marked as 0.
%
function thresholdImage = thresholdFilter(imageMatrix, value)
    imageDimensions = size(imageMatrix);
    thresholdImage = zeros(imageDimensions);
    for rowIndex = 1:imageDimensions(1)
        for columnIndex = 1:imageDimensions(2)
            if imageMatrix(rowIndex, columnIndex) > value
                thresholdImage(rowIndex, columnIndex) = 1;
            end
        end
    end
end

%
% This function isolates and catalogs blobs in the given image.
% The function passes over the image in alternating directions.
%
% It is assumed that the image given is a binary image. 
%
function blobImage = blobIdentification(imageMatrix)
    % Unassigned is marked as -1
    imageDimensions = size(imageMatrix);
    blobImage = imageMatrix;
    blobImage(blobImage > 0) = -1;
    pcolor(blobImage);
    
    blobStartIndex = 1;
    totalPasses = 2;
    for currentPass = 1:totalPasses
        % Checks all pixels, row and column indices order alternate
        for rowIndex = 1 + (mod(currentPass, 2)) * (imageDimensions(1) - 1):-1 + 2*(mod(currentPass + 1, 2)):1 + (mod(currentPass + 1, 2)) * (imageDimensions(1) - 1)
            for columnIndex = 1 + (mod(currentPass, 2)) * (imageDimensions(2) - 1):-1 + 2*(mod(currentPass + 1, 2)):1 + (mod(currentPass + 1, 2)) * (imageDimensions(2) - 1)
                % Operates on foreground objects
                if blobImage(rowIndex, columnIndex) ~= 0
                    lowestNeighbor = blobStartIndex; % We want to merge this value with the lowest value neighboring blob    
                    % 8 connectivity
                    for rowCheck = -1:1
                        for columnCheck = -1:1
                        currentRow = rowCheck + rowIndex;
                        currentColumn = columnCheck + columnIndex;
                        % for all neighbors, this pixel should take on the
                        % lowest colonized value, otherwise colonize
                        % current pixel
                        if (min(currentRow, imageDimensions(1)) == max(currentRow, 1)) && (min(currentColumn, imageDimensions(2)) == max(currentColumn, 1)) % Clever bounds checking at https://www.mathworks.com/matlabcentral/answers/106080-how-to-make-matlab-ignore-indices-that-are-out-of-bounds-for-a-matrix
                            % Compares with current, looking for colonized
                            % cells (not -1 or 0)
                            if (blobImage(currentRow, currentColumn) > 0) && (blobImage(currentRow, currentColumn) < lowestNeighbor)
                                lowestNeighbor = blobImage(currentRow, currentColumn);
                            end
                        end
                        end
                    end
                    if lowestNeighbor == blobStartIndex
                        blobStartIndex = blobStartIndex + 1;
                    end
                    blobImage(rowIndex, columnIndex) = lowestNeighbor;
                end
            end
        end
    end
end

%
% This function kills all blobs that lie on the boundary of the image.
%
% It is assumed that the imageMatrix is a binary image where 0 is the
% background and any other value greater than 0 is in the foreground.
%
function trimmedBlobImage = killEdgeBlobs(imageMatrix, borderWidth)
    imageDimensions = size(imageMatrix);
    trimmedBlobImage = blobIdentification(imageMatrix);
    
    killList = [];
    
    % Identifies identities on vertical border
    for rowIndex = 1:imageDimensions(1)
        for leftColumnSearch = 1:borderWidth
            if (~ismember(trimmedBlobImage(rowIndex, leftColumnSearch), killList) && (trimmedBlobImage(rowIndex, leftColumnSearch) ~= 0))
                killList = [killList , trimmedBlobImage(rowIndex, leftColumnSearch)];
            end
        end
        
        for rightColumnSearch = imageDimensions(1) - borderWidth:imageDimensions(1)
            if (~ismember(trimmedBlobImage(rowIndex, rightColumnSearch),killList) && (trimmedBlobImage(rowIndex, rightColumnSearch) ~= 0))
                killList = [killList , trimmedBlobImage(rowIndex, rightColumnSearch)];
            end
        end
    end
    
    % Identifies identities on horizontal border
    for columnIndex = 3:(imageDimensions(2) - 2)
        for topRowSearch = 1:borderWidth
            if (~ismember(trimmedBlobImage(topRowSearch, columnIndex), killList) && (trimmedBlobImage(topRowSearch, columnIndex) ~= 0))
                killList = [killList , trimmedBlobImage(topRowSearch, columnIndex)];
            end
        end
        
        for bottomRowSearch = imageDimensions(2) - borderWidth:imageDimensions(2)
            if (~ismember(trimmedBlobImage(bottomRowSearch, columnIndex),killList) && (trimmedBlobImage(bottomRowSearch, columnIndex) ~= 0))
                killList = [killList , trimmedBlobImage(bottomRowSearch, columnIndex)];
            end
        end
    end
    
    % Iterates through and erases all blobs whose id's are in the kill list
    for rowIndex = 1:imageDimensions(1)
        for columnIndex = 1:imageDimensions(2)
            if ismember(trimmedBlobImage(rowIndex, columnIndex), killList)
                trimmedBlobImage(rowIndex, columnIndex) = 0;
            end
        end
    end
end

%
% This function creates an image where pixels that lie on the
% interior of a boundary are marked as high and all other pixels
% are marked as low.
%
% It is assumed that the input is a binary image where objects are
% greater than zero and the foreground is zero
%
function boundaryImage = simpleEdgeFilter(imageMatrix)
    imageDimensions = size(imageMatrix);
    boundaryImage = zeros(imageDimensions);
    % checks each pixel
    for rowIndex = 1:imageDimensions(1)
        for columnIndex = 1:imageDimensions(2)
            % pixel considered edge if it is on an object and any 8
            % neighbor is not an object
            if imageMatrix(rowIndex, columnIndex) > 0
                for rowCheck = -1:1
                    for columnCheck = -1:1
                        currentRow = rowIndex + rowCheck;
                        currentColumn = columnIndex + columnCheck;
                        if (((currentRow >= 1) && (currentRow <= imageDimensions(1))) && (currentColumn >= 1) && (currentColumn <= imageDimensions(2)))
                            if imageMatrix(currentRow, currentColumn) == 0
                                boundaryImage(rowIndex, columnIndex) = 1;
                                break; % //TODO Does not entirely break but oh well
                            end
                        end
                    end
                end
            end
        end
    end
end

%
% The hough transform detects lines by cataloging all possibilities for
% each point that is marked as an edge, points on the resulting graph
% with the highest values (where the plots of possible lines for the most
% points coincide) mark actual edges.
%
% It is assumed that the imageMatrix passed to this function
% is a binary image where high value pixels are edge pixels of some
% original pattern.
%
function houghGraph = houghTransform(imageMatrix, angleDivisions)
    imageDimensions = size(imageMatrix);
    houghGraph = zeros((max(imageDimensions) * 4), angleDivisions);
    polarR = @(x, y, theta) (x * cos(theta) + y * sin(theta));
    % Catalogs the points
    for rowIndex = 1:imageDimensions(1)
        for columnIndex = 1:imageDimensions(2)
            if imageMatrix(rowIndex, columnIndex) > 0
                % For each point catalogs all angles and associated r
                for angleIndex = 1:angleDivisions 
                    currentAngle = (pi) * (angleIndex / angleDivisions); % ranges from -pi to +pi
                    r = round(abs(polarR(columnIndex, rowIndex, currentAngle)) * 2) + 1;
                    houghGraph(r, angleIndex) = houghGraph(r, angleIndex) + 1;
                end
            end
        end
    end
end

function a = sine(time, displacement, period, timeOffset)
    periodPercent = mod(time+timeOffset,1/period)*period;
    if periodPercent<0.25 || periodPercent>0.75
        a = displacement*0.5*sin(2*pi*period*(time+timeOffset));
    else
        a = -displacement * 0.5;%displacement*0.5*sin(2*pi*period*(time+timeOffset));
    end
end

function offset = getOffsetApproximation(stream)
%figure;
%plot(stream);

wrapN = @(x, N) (1 + mod(x-1, N));

% First a threshold check is preformed
threshold = 0.5 * sum(stream)/length(stream);
length(stream)
for index = 1:length(stream)
    if(stream(index) > threshold)
        stream(index) = 1;
    else
        stream(index) = 0;
    end
end
%figure;
%plot(stream);
%title('Threshold Applied');
%ylim([0,1.5]);

% Then the datastream must be eroded to make sure that all of the lines
% are clean
checkRadius = 10;
newStream = ones(length(stream),1);
for index = 1:length(stream)
    for checkIndex = -checkRadius:checkRadius
        currentIndex = wrapN((index + checkIndex),length(stream));
        if(stream(currentIndex) == 0)
            newStream(index) = 0;
            break
        end
    end
end
%figure;
%plot(newStream);
%title('Eroded Data Stream');
%ylim([0,1.5]);

% Ultra brute force method
scoresVector = zeros(1, length(newStream));
for index = 1:length(newStream)
    for expansion = 1:length(newStream)
        frontPoint = wrapN(index + expansion,length(newStream));
        backPoint = wrapN((index - expansion),length(newStream));
        if newStream(frontPoint) == newStream(backPoint)
            scoresVector(index) = scoresVector(index) + 1;
        end
    end
end

%plot(scoresVector);
minVal = max(scoresVector);
offset = find(scoresVector == minVal);
offset = offset(1);
offset = (offset / length(newStream)); %* 2 * 3.1415926535; % normalizes
if offset < 0.5
    offset = offset + 0.5; % Adds half a period so everything is the same
end

% Now, points of interest are loaded
%pointsOfInterest = [];
%for index = 1:length(newStream)
%    if(newStream(index) ~= newStream(wrapN((index + 1),length(newStream))))
%        pointsOfInterest = [pointsOfInterest,index];
%    end
%end
%figure;
%scatter(pointsOfInterest, ones(1,length(pointsOfInterest)));
%title('Points of Interest');

%
%Finally, these points are compared to find the best axis of symmetry
%TODO this is currently brute force, I need to find a better approach
%locationScore = zeros(1, length(stream));
%for bruteIndex = 1:length(stream)
    % Sorts points by distance
    % Tallies up the points
%        locationScore(bruteIndex) = locationScore(bruteIndex) + ()^2;
%    end
%end


% Voting method for finding axis of symmetry
%
%n = length(pointsOfInterest);
%k = 2;
%symmetryAxes = zeros(1, 2 * (factorial(n) / (factorial(k) * factorial(n - k))));
%counterVar = 1;
%for baseIndex = 1:length(pointsOfInterest) - 1
%    for targetIndex = 1:length(pointsOfInterest) - 1
%        if baseIndex ~= targetIndex
%            symmetryAxes(counterVar) = (pointsOfInterest(targetIndex) + pointsOfInterest(baseIndex)) / 2;
%            symmetryAxes(counterVar + 1) = mod((symmetryAxes(counterVar) + (length(stream) / 2)), length(stream));
%            counterVar = counterVar + 2;
%        end
%    end
%end
%sortedAxes = sort(symmetryAxes)
%scatter(sortedAxes,ones(1,length(sortedAxes)));

%minVal = min(locationScore);
%minIndex = find(locationScore == minVal);
%offset = sortedAxes(length(sortedAxes) / 2);
end

% Code that I borrowed, will remove later

function [TR,TT,data] = icp(model,data,maxIter,minIter,critFun,thres)
% ICP (iterative closest point) algorithm
%
%        # point-to-point distance minimization
%
%        # robust criterion function using IRLS (optional)
%
%
%   Simple usage (least-squares minimization):
%
%   [R,T,data2] = icp(model,data)
%
%   ICP fits points in data to the points in model.
%   (default) Fit with respect to minimize the sum of square
%   errors with the closest model points and data points.
%   (optional) Using a robust criterion function
%
%   INPUT:
%
%   model - matrix with model points, [ X_1 X_2 ... X_M ]
%   data - matrix with data points,   [ P_1 P_2 ... P_N ]
%
%   OUTPUT:
%
%   R - rotation matrix
%   T - translation vector
%   data2 - matrix with transformed data points,   [ P_1 P_2 ... P_N ]
%
%           data2 = R*data + T
%
%
%   Usage:
%
%   [R,T,data2] = icp(model,data,maxIter,minIter,critFun,thres)
%
%   INPUT:
%
% 	maxIter - maximum number of iterations. Default = 100
%
% 	minIter - minimum number of iterations. Default = 5
%
%   critFun  -  0 Fit with respect to minimize the sum of square errors. (default)
%               1 Huber criterion function (robust)
%               2 Tukey's bi-weight criterion function (robust)
%               3 Cauchy criterion function (robust)
%               4 Welsch criterion function (robust)
%
% 	thres - error differens threshold to stop iterations. Default = 1e-5
%
%   m-file can be downloaded for free at
%   http://www.mathworks.com/matlabcentral/fileexchange/12627-iterative-closest-point-method
%
%   icp version 1.6
%
%   written by Per Bergstrm 2016-12-11
%
% Reference:
%
% Bergstrm, P. and Edlund, O. 2014, 'Robust registration of point sets using iteratively reweighted least squares'
% Computational Optimization and Applications, vol 58, no. 3, pp. 543-561, 10.1007/s10589-014-9643-2
%


% Check input arguments

if nargin<2
    
    error('To few input arguments');
    
elseif nargin<6
    
    thres=1e-5;                     % threshold to stop icp iterations
    if nargin<5
        critFun=0;                  % critFun method, LS
        if nargin<4
            minIter=5;              % min number of icp iterations
            if nargin<3
                maxIter=100;        % max number of icp iterations
            end
        end
    end
    
end

if or(isempty(model),isempty(data))
    error('Something is wrong with the model points and data points');
end

% Use default values

if isempty(maxIter)
    maxIter=100;
end

if isempty(minIter)
    minIter=5;
end

if isempty(critFun)
    critFun=0;
end

if isempty(thres)
    thres=1e-5;
end

% Size of model points and data points

if (size(model,2)<size(model,1))
    mTranspose=true;
    m=size(model,2);
    M=size(model,1);
else
    mTranspose=false;
    m=size(model,1);
    M=size(model,2);
end

if (size(data,2)<size(data,1))
    data=data';
end

if m~=size(data,1)
    error('The dimension of the model points and data points must be equal');
end

N=size(data,2);

% Create closest point search structure

%if false % m < 4
%    if mTranspose
%        DT=delaunayTriangulation(model);
%   else
%        DT=delaunayTriangulation(model');
%    end
%else
%
    DT=[];
    resid=zeros(N,1);
    vi=ones(N,1);
%end

% Initiate weights (Only for robust criterion)

if critFun>0
    wghs=ones(N,1);
end

% Initiate transformation

TR=eye(m);
TT=zeros(m,1);

% Start the ICP algorithm

res=9e99;

for iter=1:maxIter
    
    oldres=res;
    
    % Find closest model points to data points
    if isempty(DT)
        if mTranspose
            for i=1:N
                mival=9e99;
                for j=1:M
                    val=norm(data(:,i)-model(j,:)');
                    if val<mival
                        mival=val;
                        vi(i)=j;
                        resid(i)=val;
                    end
                end
            end
        else
            for i=1:N
                mival=9e99;
                for j=1:M
                    val=norm(data(:,i)-model(:,j));
                    if val<mival
                        mival=val;
                        vi(i)=j;
                        resid(i)=val;
                    end
                end
            end
        end
    else
        [vi,resid] = nearestNeighbor(DT,data');
    end
    
    % Find transformation
    
    switch critFun
        
        case 0
            
            res=mean(resid.^2);
            
            med=mean(data,2);
            if mTranspose
                mem=mean(model(vi,:),1);
                C=data*model(vi,:)-(N*med)*mem;
                [U,~,V]=svd(C);
                Ri=V*U';
                if det(Ri)<0
                    V(:,end)=-V(:,end);
                    Ri=V*U';
                end
                Ti=mem'-Ri*med;
            else
                mem=mean(model(:,vi),2);
                C=data*model(:,vi)'-(N*med)*mem';
                [U,~,V]=svd(C);
                Ri=V*U';
                if det(Ri)<0
                    V(:,end)=-V(:,end);
                    Ri=V*U';
                end
                Ti=mem-Ri*med;
            end
            
        otherwise
            
            % Estimation of bound which 80% of data is less than
            kRob = 1.9*median(resid);
            
            maxResid=max(resid);
            if kRob<1e-6*maxResid
                kRob=0.3*maxResid;
            elseif maxResid==0
                kRob=1;
            end
            
            res=mean(resid(resid<1.5*kRob).^2);
            
            switch critFun
                case 1
                    % Huber
                    kRob=2.0138*kRob;
                    for i=1:N
                        if resid(i)<kRob
                            wghs(i)=1;
                        else
                            wghs(i)=kRob/resid(i);
                        end
                    end
                case 2
                    % Tukey's bi-weight
                    kRob=7.0589*kRob;
                    for i=1:N
                        if resid(i)<kRob
                            wghs(i)=(1-(resid(i)/kRob)^2)^2;
                        else
                            wghs(i)=0;
                        end
                    end
                case 3
                    % Cauchy
                    kRob=4.3040*kRob;
                    wghs=1./(1+(resid/kRob).^2);
                case 4
                    % Welsch
                    kRob=4.7536*kRob;
                    wghs=exp(-(resid/kRob).^2);
                otherwise
                    % Huber
                    kRob=2.0138*kRob;
                    for i=1:N
                        if resid(i)<kRob
                            wghs(i)=1;
                        else
                            wghs(i)=kRob/resid(i);
                        end
                    end
            end
            
            suWghs=sum(wghs);
            
            med=(data*wghs)/suWghs;
            if mTranspose
                mem=(wghs'*model(vi,:))/suWghs;
                C=data*(model(vi,:).*repmat(wghs,1,m))-(suWghs*med)*mem;
                [U,~,V]=svd(C);
                Ri=V*U';
                if det(Ri)<0
                    V(:,end)=-V(:,end);
                    Ri=V*U';
                end
                Ti=mem'-Ri*med;
            else
                mem=(model(:,vi)*wghs)/suWghs;
                C=(data.*repmat(wghs',m,1))*model(:,vi)'-(suWghs*med)*mem';
                [U,~,V]=svd(C);
                Ri=V*U';
                if det(Ri)<0
                    V(:,end)=-V(:,end);
                    Ri=V*U';
                end
                Ti=mem-Ri*med;
            end
            
    end
    
    data=Ri*data;                       % Apply transformation
    for i=1:m
        data(i,:)=data(i,:)+Ti(i);      %
    end
    
    TR=Ri*TR;                           % Update transformation
    TT=Ri*TT+Ti;                        %
    
    if iter >= minIter
        if abs(oldres-res) < thres
            break
        end
    end
    
end
end