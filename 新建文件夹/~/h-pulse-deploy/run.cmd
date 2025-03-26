@echo off
title H-Pulse·Mirage 部署向导
echo ===========================================
echo       H-Pulse·Mirage 一键部署向导
echo ===========================================
echo.
echo 此向导将帮助您部署H-Pulse·Mirage命运模拟与演出引擎。
echo.
echo 请确保：
echo  1. 已安装Docker Desktop并启动
echo  2. 系统有足够的磁盘空间(至少10GB)
echo.
echo ===========================================
echo.

:MENU
echo 请选择操作:
echo [1] 部署系统
echo [2] 停止服务
echo [3] 删除所有数据并停止服务
echo [4] 查看帮助文档
echo [5] 退出
echo.
set /p choice=请输入选项(1-5): 

if "%choice%"=="1" goto DEPLOY
if "%choice%"=="2" goto STOP
if "%choice%"=="3" goto DELETE
if "%choice%"=="4" goto HELP
if "%choice%"=="5" goto END
echo 无效选择，请重新输入
goto MENU

:DEPLOY
echo.
echo 正在启动部署流程...
powershell -ExecutionPolicy Bypass -File "%~dp0deploy.ps1"
echo.
echo 按任意键返回主菜单...
pause > nul
goto MENU

:STOP
echo.
echo 正在停止服务...
cd %~dp0h_pulse_mirage
docker-compose down
echo 服务已停止
echo.
echo 按任意键返回主菜单...
pause > nul
goto MENU

:DELETE
echo.
echo 警告: 这将删除所有数据，包括数据库和配置!
echo.
set /p confirm=确认操作? (y/n): 
if /i not "%confirm%"=="y" goto MENU
cd %~dp0h_pulse_mirage
docker-compose down -v
echo 所有服务和数据已删除
echo.
echo 按任意键返回主菜单...
pause > nul
goto MENU

:HELP
echo.
start "" "%~dp0README.md"
echo 已打开帮助文档
echo.
echo 按任意键返回主菜单...
pause > nul
goto MENU

:END
echo.
echo 感谢使用H-Pulse·Mirage部署向导。
echo.
timeout /t 3 > nul 