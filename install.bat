@echo off

@REM this temporary until git is installed in the lab, also dependent on version number (app-3.3.6)
SET git="C:\Users\%USERNAME%\AppData\Local\GithubDesktop\app-3.3.6\resources\app\git\git.exe"

@REM https://stackoverflow.com/a/8995407
NET SESSION >nul 2>&1
IF NOT %errorlevel% EQU 0 (
    ECHO Please escalate permsission to administrator ^(please run as admin^)
    PAUSE

    @REM exit program and returning error code 1 (program failed to run)
    exit /b 1
)

@REM program has administrator privilege, continue.

@REM ensure required commands are installed
%git% --version
IF NOT %errorlevel% EQU 0 (
    ECHO git is not installed, please install git to continue
    PAUSE

    exit /b 1
)

SET BINDIR="C:\Users\%USERNAME%\.bin" 

@REM create location to install control-panel git repo (i.e. source code)
IF NOT EXIST %BINDIR% mkdir %BINDIR%

cd %BINDIR%
%git% clone https://github.com/timberline-secondary/control-panel

@REM per https://stackoverflow.com/a/41809116, move batch file to System32
@REM also, writing to System32 requires administrator override
copy %BINDIR%\control-panel\control-panel.bat C:\Windows\System32\control-panel.bat

@REM alias of ctrlp for short-hand
copy %BINDIR%\control-panel\control-panel.bat C:\Windows\System32\ctrlp.bat 
