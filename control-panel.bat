@echo off
cd C:\Users\%USERNAME%\.bin\control-panel

@REM temporary variable for python path until python is installed in PATH, is version dependant (Python311)
SET python="C:\Program Files\Python311\python.exe"


ECHO:
@REM ### update git ### ------------>>>
ECHO ### PULLING FROM GITHUB ###
git pull

IF NOT %errorlevel% EQU 0 (
    ECHO something went wrong while pulling from git.
    PAUSE

    exit /b 1
)
ECHO ### PULLED FROM GITHUB ###


ECHO:
@REM ### install python env ### ------------>>>
IF NOT EXIST %BINDIR% (
    ECHO ### INSTALLING PYTHON ENVIRONMENT ###
    %python% -m venv %BINDIR%\env
    IF NOT %errorlevel% EQU 0 (
        ECHO something went wrong while running installing python venv
        PAUSE
        
        exit /b 1
    )

    ECHO ### INSTALLED PYTHON ENVIRONMENT ###
)


ECHO:
@REM activate venv
ECHO ### ACTIVATING PYTHON ENVIRONMENT ###
%BINDIR%\env\Scripts\activate

IF NOT %errorlevel% EQU 0 (
    ECHO something went wrong while activating venv
    PAUSE
    
    exit /b 1
)
ECHO ### ACTIVATED PYTHON ENVIRONMENT ###


ECHO:
@REM ### update pip deps ### ------------>>>
ECHO ### UPDATING PIP DEPENDANCIES ###
%python% -m pip install -r requirements.txt

IF NOT %errorlevel% EQU 0 (
    ECHO something went wrong while updating pip deps.
    PAUSE

    exit /b 1
)
ECHO ### DEPENDANCIES UPDATED ###

@START %python% %BINDIR%\control-panel\main.py