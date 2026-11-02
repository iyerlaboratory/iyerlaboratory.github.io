import sys, os, shutil
from PIL import Image, ImageOps
sys.path.insert(0, os.path.dirname(__file__))
from collage import collage_fixed as collage
date, files = sys.argv[1], sys.argv[2:]
out = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'news', date); os.makedirs(out, exist_ok=True)
collage(files, f'{out}/collage.jpg')
for i, f in enumerate(files, 1):
    im = ImageOps.exif_transpose(Image.open(f)).convert('RGB'); im.thumbnail((1800, 1800))
    im.save(f'{out}/{i}.jpg', quality=85, optimize=True, progressive=True)
c = Image.open(f'{out}/collage.jpg'); t = c.copy(); t.thumbnail((800, 800))
t.save(f'{out}/collage-thumb.jpg', quality=84, optimize=True, progressive=True)
print(date, c.size, sorted(os.listdir(out)))
