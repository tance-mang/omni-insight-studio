import os
from pathlib import Path

def shuju_mulu():
    path = Path(os.environ.get('XHS_DATA_DIR', str(Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'XHSInsightStudio')))
    path.mkdir(parents=True, exist_ok=True)
    return path
