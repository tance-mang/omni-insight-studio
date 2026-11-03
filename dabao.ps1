$ErrorActionPreference = 'Stop'
& .\.venv\Scripts\python -m PyInstaller --noconfirm --name XHS_Insight_Studio --collect-all streamlit --collect-all sqlalchemy --copy-metadata streamlit --add-data 'app.py;.' --add-data 'jiemian.py;.' --add-data 'hexin.py;.' --add-data 'shujuku.py;.' --add-data 'peizhi.py;.' qidong.py
if ($LASTEXITCODE -ne 0) { throw '打包失败' }
Copy-Item README.md,LICENSE,使用说明.md -Destination dist\XHS_Insight_Studio
& .\.venv\Scripts\python shouji_xuke.py dist\XHS_Insight_Studio
Compress-Archive -Path dist\XHS_Insight_Studio -DestinationPath dist\XHS_Insight_Studio-Windows.zip -Force
