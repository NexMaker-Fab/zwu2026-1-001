@echo off
chcp 65001 >nul
echo ========================================
echo    正在打包作业上传系统为 .exe
echo ========================================
echo.
echo 这可能需要几分钟，请耐心等待...
echo.

REM 打包服务器
python -m PyInstaller --onefile --name="作业上传系统" --windowed --add-data="index.html;." --add-data="team.html;." --add-data="homework.html;." --add-data="final-work.html;." --add-data="member-caiaomi.html;." --add-data="member-caiyitong.html;." --add-data="member-chenguo.html;." --add-data="member-wangyuhan.html;." --add-data="style-new.css;." --icon=NONE "github web.py"

echo.
echo ========================================
echo 打包完成！
echo 可执行文件在 dist 文件夹中：
echo   dist\作业上传系统.exe
echo ========================================
pause
