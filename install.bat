@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title STP installer

set "UNATTENDED=0"
if /i "%~1"=="--unattended" set "UNATTENDED=1"

call :find_python
if defined PY goto have_python

where winget >nul 2>&1
if errorlevel 1 goto no_winget

call winget install -e --id Python.Python.3.13 --scope user --silent --accept-package-agreements --accept-source-agreements
if errorlevel 1 call winget install -e --id Python.Python.3.13 --silent --accept-package-agreements --accept-source-agreements
call :find_python
if defined PY goto have_python

echo Python was installed but this window cannot see it yet.
echo Close this window and run install.bat again.
goto fail

:no_winget
start "" "https://www.python.org/downloads/"
echo Install Python 3.10 or newer from https://www.python.org/downloads/
echo Tick "Add python.exe to PATH" in the installer, then run install.bat again.
goto fail

:have_python
set "VENV_PY=venv\Scripts\python.exe"
if exist "%VENV_PY%" (
    "%VENV_PY%" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
    if not errorlevel 1 goto venv_ready
)
if exist "venv" rmdir /s /q "venv"
%PY% -m venv "venv"
if errorlevel 1 goto fail_venv

:venv_ready
"%VENV_PY%" -m pip install --upgrade pip >nul 2>&1
"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 goto fail_pip

if not exist ".env" if exist ".env.example" copy ".env.example" ".env" >nul

if "%UNATTENDED%"=="1" exit /b 0

set "ANS="
set /p "ANS=Start STP now? [Y/n] "
if /i "%ANS%"=="n" goto done
if /i "%ANS%"=="no" goto done
call "%~dp0start.bat"
exit /b %errorlevel%

:done
pause
exit /b 0

:fail_venv
echo ERROR: could not create the virtual environment.
goto fail

:fail_pip
echo ERROR: installing dependencies failed, check your internet connection and the messages above.
goto fail

:fail
if not "%UNATTENDED%"=="1" pause
exit /b 1

:find_python
set "PY="
call :try_cmd "py -3"
call :try_cmd "python"
call :try_cmd "python3"
call :try_exe "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
call :try_exe "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
call :try_exe "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
call :try_exe "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
call :try_exe "%ProgramFiles%\Python313\python.exe"
exit /b 0

:try_cmd
if defined PY exit /b 0
set "PY=%~1"
call :check_py
if errorlevel 1 set "PY="
exit /b 0

:try_exe
if defined PY exit /b 0
if not exist "%~1" exit /b 0
set "PY="%~1""
call :check_py
if errorlevel 1 set "PY="
exit /b 0

:check_py
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
exit /b %errorlevel%
