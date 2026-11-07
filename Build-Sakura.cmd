@echo off
setlocal
cd /d "%~dp0"
if not defined JAVA_HOME if exist "C:\Program Files\Android\Android Studio\jbr\bin\java.exe" set "JAVA_HOME=C:\Program Files\Android\Android Studio\jbr"
call gradlew.bat :app:assembleDebug :app:lintDebug --max-workers=1 --no-watch-fs -Dorg.gradle.internal.instrumentation.agent=false --console=plain
if errorlevel 1 exit /b %errorlevel%
if not exist artifacts mkdir artifacts
copy /y app\build\outputs\apk\debug\app-debug.apk artifacts\Sakura-Sunset-1.2.0-debug.apk >nul
echo APK: %~dp0artifacts\Sakura-Sunset-1.2.0-debug.apk
