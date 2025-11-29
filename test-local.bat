@echo off
REM ChangeFace3 Windows 本地测试脚本

echo ====================================
echo ChangeFace3 本地测试脚本 (Windows)
echo ====================================
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

echo 项目目录: %CD%
echo.

REM ==================== 检查 Python ====================
echo 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python 未安装或未添加到 PATH
    pause
    exit /b 1
)

python --version
echo.

REM ==================== 检查/创建虚拟环境 ====================
echo 检查虚拟环境...

if not exist "venv" (
    echo [警告] 虚拟环境不存在，正在创建...
    python -m venv venv
    echo [成功] 虚拟环境创建成功
) else (
    echo [成功] 虚拟环境已存在
)
echo.

REM ==================== 激活虚拟环境 ====================
echo 激活虚拟环境...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo [错误] 虚拟环境激活失败
    pause
    exit /b 1
)

echo [成功] 虚拟环境已激活
echo.

REM ==================== 检查/安装依赖 ====================
echo 检查依赖包...

if not exist "requirements.txt" (
    echo [错误] requirements.txt 不存在
    pause
    exit /b 1
)

REM 检查是否需要安装 streamlit
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo [警告] 缺少依赖包，正在安装...
    pip install -r requirements.txt -q
    echo [成功] 依赖包安装完成
) else (
    echo [成功] 依赖已安装
)
echo.

REM ==================== 检查配置文件 ====================
echo 检查配置文件...

REM 检查 .env 文件
if not exist ".env" (
    echo [警告] .env 文件不存在
    if exist ".env.example" (
        echo    正在从 .env.example 创建 .env...
        copy .env.example .env >nul
        echo [成功] .env 文件已创建
        echo [警告] 请编辑 .env 文件，配置 REPLICATE_API_TOKEN
    ) else (
        echo [错误] .env.example 也不存在
    )
) else (
    echo [成功] .env 文件存在
)
echo.

REM 检查 users.txt 文件
if not exist "users.txt" (
    echo [警告] users.txt 文件不存在
    if exist "users.txt.example" (
        echo    正在从 users.txt.example 创建 users.txt...
        copy users.txt.example users.txt >nul
        echo. >> users.txt
        echo # 默认管理员账号（请修改密码） >> users.txt
        echo admin:admin123 >> users.txt
        echo [成功] users.txt 文件已创建
        echo [警告] 默认账号: admin / admin123 (请修改密码)
    ) else (
        echo [错误] users.txt.example 也不存在
    )
) else (
    echo [成功] users.txt 文件存在
)
echo.

REM ==================== 检查必要文件 ====================
echo 检查必要文件...

set "ALL_FILES_EXIST=1"

if exist "app.py" (
    echo [成功] app.py
) else (
    echo [错误] app.py 缺失
    set "ALL_FILES_EXIST=0"
)

if exist "config.py" (
    echo [成功] config.py
) else (
    echo [错误] config.py 缺失
    set "ALL_FILES_EXIST=0"
)

if exist "requirements.txt" (
    echo [成功] requirements.txt
) else (
    echo [错误] requirements.txt 缺失
    set "ALL_FILES_EXIST=0"
)

if "%ALL_FILES_EXIST%"=="0" (
    echo.
    echo [错误] 缺少必要文件，无法启动
    pause
    exit /b 1
)
echo.

REM ==================== 运行测试 ====================
echo 运行功能测试...
echo.

if exist "test_auth.py" (
    echo 测试登录功能...
    python test_auth.py
    echo.
) else (
    echo [警告] test_auth.py 不存在，跳过认证测试
    echo.
)

REM ==================== 显示项目信息 ====================
echo ====================================
echo 项目信息
echo ====================================
echo 项目目录: %CD%
python --version
echo 虚拟环境: %VIRTUAL_ENV%
echo 监听端口: 8501
echo.

REM ==================== 启动选项 ====================
echo ====================================
echo 准备启动应用
echo ====================================
echo.
echo 选择启动方式:
echo   1) 正常启动 (默认)
echo   2) 启动并自动打开浏览器
echo   3) 调试模式启动
echo   4) 指定端口启动
echo   5) 仅检查，不启动
echo   q) 退出
echo.

set /p choice="请选择 (1-5 or q): "

if "%choice%"=="" set choice=1

if "%choice%"=="1" goto start_normal
if "%choice%"=="2" goto start_browser
if "%choice%"=="3" goto start_debug
if "%choice%"=="4" goto start_custom_port
if "%choice%"=="5" goto check_only
if /i "%choice%"=="q" goto quit

echo.
echo [错误] 无效选择
pause
exit /b 1

:start_normal
echo.
echo [启动] Streamlit 应用...
echo ====================================
echo.
echo 访问地址: http://localhost:8501
echo 停止应用: Ctrl+C
echo.
streamlit run app.py --server.address=localhost --server.port=8501
goto end

:start_browser
echo.
echo [启动] 应用并打开浏览器...
echo.
streamlit run app.py --server.address=localhost --server.port=8501 --server.headless=false
goto end

:start_debug
echo.
echo [启动] 调试模式...
echo.
echo [提示] 文件修改会自动重载
echo.
streamlit run app.py --server.address=localhost --server.port=8501 --logger.level=debug
goto end

:start_custom_port
echo.
set /p CUSTOM_PORT="请输入端口号: "
echo.
echo [启动] 在端口 %CUSTOM_PORT% 启动应用...
echo.
streamlit run app.py --server.address=localhost --server.port=%CUSTOM_PORT%
goto end

:check_only
echo.
echo [成功] 检查完成，未启动应用
echo.
echo 手动启动命令:
echo   venv\Scripts\activate.bat
echo   streamlit run app.py
echo.
pause
exit /b 0

:quit
echo.
echo 退出
exit /b 0

:end
pause
