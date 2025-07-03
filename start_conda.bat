@echo off
chcp 65001 >nul
echo 🇩🇪 德国入籍考试学习助手 (Conda版本)
echo ==================================================

REM 检查conda环境
if not exist ".conda\python.exe" (
    echo ❌ 未找到conda环境，请先创建conda环境
    pause
    exit /b 1
)

echo ✅ 找到conda环境: .conda\python.exe

REM 启动后端服务
echo 🚀 启动后端服务...
start "后端API" cmd /k ".conda\python.exe app.py"

REM 等待3秒
timeout /t 3 /nobreak >nul

REM 启动前端服务
echo 🚀 启动前端服务...
start "前端界面" cmd /k ".conda\python.exe -m streamlit run streamlit_app.py --server.port 8501"

REM 等待5秒后打开浏览器
timeout /t 5 /nobreak >nul
echo 🌐 正在打开浏览器...
start http://localhost:8501

echo.
echo ✅ 服务已启动！
echo 后端API: http://localhost:8000
echo 前端界面: http://localhost:8501
echo API文档: http://localhost:8000/docs
echo.
echo 按任意键退出...
pause >nul 