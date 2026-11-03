"""Copy installed dependency license texts into a distributable folder."""
from importlib.metadata import distributions
from pathlib import Path
import shutil
import sys

target=Path(sys.argv[1]) / '第三方许可'
for dist in distributions():
    for file in dist.files or []:
        if any(token in file.name.lower() for token in ['license','copying','notice']):
            source=Path(dist.locate_file(file))
            if source.is_file():
                dest=target / dist.metadata['Name'] / str(file).replace('..','_')
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(source,dest)
