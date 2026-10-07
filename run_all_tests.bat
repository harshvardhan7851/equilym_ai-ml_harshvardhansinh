@echo off
echo ================================================================================
echo Running All Test Suites
echo ================================================================================
echo.

echo [1/5] Running Phase 1 Tests (Data Loading)...
python tests/test_phase1.py
if %errorlevel% neq 0 (
    echo FAILED: Phase 1 tests failed
    pause
    exit /b 1
)
echo.

echo [2/5] Running Phase 2 Tests (Trend Detection)...
python tests/test_phase2.py
if %errorlevel% neq 0 (
    echo FAILED: Phase 2 tests failed
    pause
    exit /b 1
)
echo.

echo [3/5] Running Phase 3 Tests (Outlier Detection)...
python tests/test_phase3.py
if %errorlevel% neq 0 (
    echo FAILED: Phase 3 tests failed
    pause
    exit /b 1
)
echo.

echo [4/5] Running Phase 4 Tests (Correlation Analysis)...
python tests/test_phase4.py
if %errorlevel% neq 0 (
    echo FAILED: Phase 4 tests failed
    pause
    exit /b 1
)
echo.

echo [5/5] Running Phase 5 Tests (Insight Generation)...
python tests/test_phase5.py
if %errorlevel% neq 0 (
    echo FAILED: Phase 5 tests failed
    pause
    exit /b 1
)
echo.

echo ================================================================================
echo SUCCESS: All test suites passed!
echo ================================================================================
pause
