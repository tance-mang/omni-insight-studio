import sys
from pathlib import Path
from streamlit.web import cli

if __name__ == '__main__':
    root=Path(getattr(sys,'_MEIPASS',Path(__file__).parent))
    sys.argv=['streamlit','run',str(root/'app.py'),'--server.address=127.0.0.1','--server.port=18501','--global.developmentMode=false']
    sys.exit(cli.main())
