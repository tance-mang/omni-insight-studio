import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path
from streamlit.web import cli

if __name__ == '__main__':
    root=Path(getattr(sys,'_MEIPASS',Path(__file__).parent))
    def dakai():
        for _ in range(60):
            try:
                with urllib.request.urlopen('http://127.0.0.1:18501/_stcore/health',timeout=1) as response:
                    if response.status == 200:
                        webbrowser.open('http://127.0.0.1:18501'); return
            except OSError: time.sleep(1)
    threading.Thread(target=dakai,daemon=True).start()
    sys.argv=['streamlit','run',str(root/'app.py'),'--server.address=127.0.0.1','--server.port=18501','--server.headless=true','--browser.gatherUsageStats=false','--global.developmentMode=false']
    sys.exit(cli.main())
