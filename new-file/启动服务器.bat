@echo off
chcp 65001 >nul
echo ========================================
echo    这是啥组 - 作业上传系统
echo ========================================
echo.
echo 正在启动服务器...
echo.
python3 server.py
if errorlevel 1 (
    echo.
    echo Python3 启动失败，尝试使用 python...
    python server.py
)
pause