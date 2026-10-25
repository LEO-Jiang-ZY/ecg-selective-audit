@echo off
chcp 65001 >nul
cd /d "%~dp0"

set LECTRACE=C:\Users\24958\.workbuddy\binaries\python\envs\ptbxl\Scripts\lectrace.exe

echo ==========================================
echo  Step 1 / 2   重新构建演示站点
echo ==========================================
"%LECTRACE%" build --output site\lectrace
if errorlevel 1 (
    echo.
    echo [失败] 构建出错，请把上面的报错发给我。
    pause
    exit /b 1
)

echo.
echo ==========================================
echo  Step 2 / 2   提交并推送
echo ==========================================
echo 接下来在 GitHub Desktop 里做两件事：
echo   1. 左下 Summary 填一句说明，点 Commit to main
echo   2. 顶部点 Push origin
echo.
echo 推送后 Vercel 约 30 秒自动更新，GitHub Pages 约 1-2 分钟。
echo.
pause
