@echo off
echo AutoEDA Pro baslatiliyor...
echo.

:: Ollama'yi kontrol et
echo Ollama kontrol ediliyor...
tasklist /fi "imagename eq ollama.exe" | find "ollama.exe" >nul
if errorlevel 1 (
    echo Ollama baslatiliyor...
    start "" "ollama" serve
    timeout /t 3 /nobreak >nul
) else (
    echo Ollama zaten calisiyor!
)

:: Sanal ortami aktif et ve uygulamayı başlat
echo.
echo Uygulama baslatiliyor...
call venv\Scripts\activate
streamlit run app.py

pause