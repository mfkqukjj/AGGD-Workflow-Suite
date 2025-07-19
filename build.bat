@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

echo 开始打包程序...

:: 清理旧的构建文件
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

:: 执行打包
pyinstaller build_config.spec --noconfirm

:: 检查是否打包成功
if %errorlevel% equ 0 (
    :: 设置路径变量
    set "DIST_PATH=%CD%\dist"
    set "LAUNCHER_NAME=启动AGGD工作流套件.bat"
    
    :: 创建启动器
    echo @echo off > "!DIST_PATH!\!LAUNCHER_NAME!"
    echo cd /d "%%~dp0\AGGD-Workflow-Suite" >> "!DIST_PATH!\!LAUNCHER_NAME!"
    echo start AGGD-Workflow-Suite.exe >> "!DIST_PATH!\!LAUNCHER_NAME!"
    echo exit >> "!DIST_PATH!\!LAUNCHER_NAME!"
    
    :: 创建桌面快捷方式
    set "SHORTCUT_SCRIPT=%TEMP%\create_shortcut.vbs"
    (
        echo Set WS = CreateObject^("WScript.Shell"^)
        echo Set lnk = WS.CreateShortcut^("%USERPROFILE%\Desktop\AGGD工作流套件.lnk"^)
        echo lnk.TargetPath = "%DIST_PATH%\%LAUNCHER_NAME%"
        echo lnk.WorkingDirectory = "%DIST_PATH%"
        if exist "app.ico" echo lnk.IconLocation = "%CD%\app.ico"
        echo lnk.Save
    ) > "!SHORTCUT_SCRIPT!"
    
    cscript //nologo "!SHORTCUT_SCRIPT!"
    del "!SHORTCUT_SCRIPT!"
    
    echo ============================================
    echo 打包完成！
    echo 程序目录: !DIST_PATH!\AGGD-Workflow-Suite
    echo 启动文件: !DIST_PATH!\!LAUNCHER_NAME!
    echo ============================================
) else (
    echo 打包失败，请检查错误信息。
)

endlocal
pause