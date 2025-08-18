@echo off
REM Run tests for the new provider architecture (Windows)

echo Running Provider Architecture Tests...
echo =======================================

REM Install test dependencies if needed
pip install -r requirements-test.txt

echo.
echo 1. Testing Base Provider Classes...
echo -----------------------------------
pytest tests\test_providers_base.py -v

echo.
echo 2. Testing TwelveData Provider...
echo --------------------------------
pytest tests\test_providers_twelvedata.py -v

echo.
echo 3. Testing Marketaux Provider...
echo -------------------------------
pytest tests\test_providers_marketaux.py -v

echo.
echo 4. Testing News Service...
echo ------------------------
pytest tests\test_news_service.py -v

echo.
echo 5. Running All Tests with Coverage...
echo ------------------------------------
pytest tests\test_providers*.py tests\test_news_service.py --cov=app\providers --cov=app\services\news --cov-report=term-missing

echo.
echo Test Summary:
echo =============
pytest tests\test_providers*.py tests\test_news_service.py --tb=no -q