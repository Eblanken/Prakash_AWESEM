
function [unknowns,steps,S] = GaussNewton()
%GaussNewton- uses the Gauss-Newton method to perform a non-linear least
%squares approximation for the origin of a circle of points
%  Takes as input a row vector of x and y values, and a column vector of
%  initial guesses. partial derivatives for the jacobian must entered below
%  in the df function
    format long
tol = 1e-8;
maxstep = 30;
z = 2*pi*rand(100,1);
p = cos(z);
q = sin(z);
d = ones(100,1);
a = [0.1;0.1];
m=length(p);
n=length(a);
aold = a;
for k=1:maxstep
    S = 0;
    for i=1:m
%set a value for the accuracy
%set maximum number of steps to run for
     %create 100 random points
%create a circle with those points
%set distance to origin as 1 for all points
%set initial guess for origin
%determine number of functions
%determine number of unkowns
%iterate through process
    end
end
for j=1:n
    J(i,j) = df(p(i),q(i),a(1,1),a(2,1),j); %calculate Jacobian
Jz = -JT*J;
JT(j,i) = J(i,j);
%and its trnaspose
%multiply Jacobian and
%negative transpose
for i=1:m
    r(i,1) = d(i) - sqrt((a(1,1)-p(i))^2+(a(2,1)-q(i))^2);%calculate r
    S = S + r(i,1)^2;               %calculate sum of squares of residuals
end
S
g= Jz\JT;
a= aold-g*r;
unknowns = a;
err(k) = a(1,1)-aold(1,1); if (abs(err(k)) <= tol);
break end
aold = a;
steps = k;
hold all
plot(p,q,'r*')
plot(a(1,1),a(2,1),'b*')
origin(expect it to be 0,0)
title('Gauss-Newton Approximation of Origin of Circular Data Points') %set axis
lables, title and legend
end
xlabel('X')
ylabel('Y')
legend('Data Points','Gauss-Newton Approximation of Origin')
hold off
errratio(3:k) = err(2:k-1)./err(3:k);
end
function value = df(p,q,a1,a2,index)
switch index
%calculate partials
%mulitply Jz inverse by J transpose
%calculate new approximation
    %calculate error
        %if less than tolerance break
%set aold to a
%plot the data points
%plot the approximation of the
    case 1
        value = (2*a1 - 2*p)*0.5*((a1-p)^2+(a2-q)^2)^(-0.5);
    case 2
        value = (2*a2 - 2*q)*0.5*((a1-p)^2+(a2-q)^2)^(-0.5);
end
