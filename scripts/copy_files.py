import shutil
from pathlib import Path

root = Path(r"C:\PostDoc\data\Hagedorn\temp")
export = Path(r"C:\PostDoc\data\Hagedorn\export")
export.mkdir(exist_ok=True)

for fn in root.rglob('OCR-D-EXTLINES*.png'):
    tdir = export.joinpath(fn.parents[2].name)
    tdir.mkdir(exist_ok=True)

    #shutil.copyfile("\\\\?\\" + str(fn), tdir.joinpath(str(fn.name)[str(fn.name).find('Seite'):]))
    shutil.copyfile("\\\\?\\" + str(fn), tdir.joinpath(str(fn.name)[str(fn.name).find('VD18'):]))

