@echo off
cd "C:\Users\%USERNAME%\.bin\control-panel"

SET BINDIR="C:\Users\%USERNAME%\.bin"

@REM temporary variable for python path until python is installed in PATH, is version dependant (Python311)
SET git="C:\Users\%USERNAME%\AppData\Local\GithubDesktop\app-3.3.6\resources\app\git\cmd\git.exe"
SET python="C:\Program Files\Python311\python.exe"


ECHO:
@REM ### update git ### ------------>>>
ECHO ### PULLING FROM GITHUB ###
%git% pull

IF NOT %errorlevel% EQU 0 (
    ECHO ^[ERROR^]^: Something went wrong while pulling from git.
    PAUSE

    exit /b 1
)
ECHO ### PULLED FROM GITHUB ###


ECHO:
@REM ### install python env ### ------------>>>
IF NOT EXIST %BINDIR%\control-panel\env (
    ECHO ### INSTALLING PYTHON ENVIRONMENT ###
    ECHO Creating ./env ...
    %python% -m venv %BINDIR%\control-panel\env
    IF NOT %errorlevel% EQU 0 (
        ECHO ^[ERROR^]^: something went wrong while running installing python venv.
        PAUSE
        
        exit /b 1
    )

    ECHO ### INSTALLED PYTHON ENVIRONMENT ###
)


ECHO:
@REM activate venv
ECHO ### ACTIVATING PYTHON ENVIRONMENT ###
ECHO Activating python virtual environment ...
CALL %BINDIR%\control-panel\env\Scripts\activate

IF NOT %errorlevel% EQU 0 (
    ECHO ^[ERROR^]^: Something went wrong while activating venv.
    PAUSE
    
    exit /b 1
)
ECHO ### ACTIVATED PYTHON ENVIRONMENT ###


ECHO:
@REM ### update pip deps ### ------------>>>
ECHO ### UPDATING PIP DEPENDANCIES ###
%python% -m pip install -r requirements.txt

IF NOT %errorlevel% EQU 0 (
    ECHO ^[ERROR^]^: Something went wrong while updating pip deps.
    PAUSE

    exit /b 1
)
ECHO ### DEPENDANCIES UPDATED ###

@REM ### run the python script ### ------------>>>
%python% %BINDIR%\control-panel\main.py




@REM ### CLEANUP SECTION ### ------------>>>
cd "C:\Users\%USERNAME%\"

CALL %BINDIR%\control-panel\env\Scripts\deactivate
IF NOT %errorlevel% EQU 0 (
    ECHO ^[ERROR^]^: Something went wrong while deactivating venv.
    PAUSE
    
    exit /b 1
)
