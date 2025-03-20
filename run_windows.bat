@echo off
echo Building Docker container...
docker build -t bin-packing .

echo.
echo Starting Bin Packing Web Application...
echo The application will be available at http://localhost:5000
echo.

start http://localhost:5000
docker run --rm -p 5000:5000 bin-packing

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error running the container. Make sure Docker is running.
    pause
) 