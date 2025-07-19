@echo off
chcp 65001 >nul
echo ========================================
echo     YouTube视频播放器 - 打包工具
echo ========================================
echo.
echo 正在开始打包过程...
echo.

REM 检查是否安装了PyInstaller
python -c "import pyinstaller" 2>nul
if errorlevel 1 (
    echo ❌ PyInstaller未安装，正在安装...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ 安装PyInstaller失败！
        pause
        exit /b 1
    )
)

REM 检查是否安装了webdriver-manager
python -c "import webdriver_manager" 2>nul
if errorlevel 1 (
    echo ❌ webdriver-manager未安装，正在安装...
    pip install webdriver-manager
    if errorlevel 1 (
        echo ❌ 安装webdriver-manager失败！
        pause
        exit /b 1
    )
)

echo ✅ 依赖检查完成
echo.
echo 🔨 开始打包...
echo.

REM 清理之前的构建文件
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM 使用spec文件进行打包
pyinstaller youtube_player.spec --clean

if errorlevel 1 (
    echo.
    echo ❌ 打包失败！请检查错误信息。
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ 打包完成！
echo.
echo 📁 可执行文件位置: dist\YouTube视频播放器.exe
echo.
echo 💡 使用说明:
echo   1. 将dist文件夹复制到目标电脑
echo   2. 确保目标电脑已安装Chrome浏览器
echo   3. 双击"YouTube视频播放器.exe"即可运行
echo.
echo ========================================
pause 