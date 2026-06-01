@echo off
chcp 65001 >nul
echo ========================================
echo    这是啥组 - 作业上传系统
echo ========================================
echo.
echo 正在启动服务器...
echo.
echo 服务器启动后会自动打开浏览器
echo 如果浏览器没有自动打开，请手动访问：
echo   http://localhost:8080/index.html
echo.
start http://localhost:8080/index.html
python "github web.py"
if errorlevel 1 (
    echo.
    echo Python 启动失败，尝试使用 python3...
    python3 "github web.py"
)
pause
