@echo off
echo ==========================================
echo  HealthAI Scheduler - Auto Setup & Run
echo ==========================================
echo.

:: Step 1: Create virtual environment if not exists
if not exist "venv" (
    echo [1/5] Creating virtual environment...
    python -m venv venv
) else (
    echo [1/5] Virtual environment already exists.
)

:: Step 2: Activate venv
echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

:: Step 3: Install dependencies
echo [3/5] Installing dependencies...
pip install flask flask-sqlalchemy scikit-learn pandas numpy simpy joblib --quiet

:: Step 4: Generate training data and train ML model
echo [4/5] Generating training data and training ML model...
python data\generate_data.py
python ai_modules\no_show_predictor.py

:: Step 5: Seed database and run app
echo [5/5] Seeding database and starting Flask server...
python seed_db.py

echo.
echo ==========================================
echo  Server starting at http://127.0.0.1:5000
echo  Press Ctrl+C to stop
echo ==========================================
echo.
python app.py

pause
