@echo off
echo Starting KazhaiAI MVP...
cd backend
echo Installing dependencies...
pip install -r requirements.txt
echo Running Flask App...
set FLASK_APP=app.py
set FLASK_ENV=development
python app.py
pause
