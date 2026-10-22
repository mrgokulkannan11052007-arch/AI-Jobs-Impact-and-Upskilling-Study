@echo off
cd /d "%~dp0"
echo ================================================
echo AI Jobs Impact and Upskilling Study
echo ================================================
where py >nul 2>nul
if %errorlevel%==0 (
    py -m pip install -r requirements.txt
    if errorlevel 1 goto install_error
    py -m streamlit run app.py
    goto end
)
where python >nul 2>nul
if %errorlevel%==0 (
    python -m pip install -r requirements.txt
    if errorlevel 1 goto install_error
    python -m streamlit run app.py
    goto end
)
echo Python was not detected. Install Python 3.10 or later from https://www.python.org/downloads/windows/
echo During installation, tick "Add python.exe to PATH".
pause
goto end
:install_error
echo Dependency installation failed. Check your internet connection and Python installation.
pause
:end
