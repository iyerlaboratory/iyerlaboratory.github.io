"""Make a clean collage: photos in justified rows, even white gutters, no decoration."""
import sys, math
from PIL import Image, ImageOps
def collage(paths, out, W=1600, gap=14, target_h=None, plan=None):
    ims=[ImageOps.exif_transpose(Image.open(p)).convert('RGB') for p in paths]
    n=len(ims)
    # rows: 1-2 photos in one row; 3 = 1 big + 2; 4 = 2+2; 5 = 2+3; 6 = 3+3; more = rows of 3
    plans={1:[1],2:[2],3:[1,2],4:[2,2],5:[2,3],6:[3,3]}
    rows=plan or plans.get(n) or [3]*(n//3)+([n%3] if n%3 else [])
    # landscape pair reads better stacked when both are portrait? keep side by side
    canvas_rows=[]; i=0; H=0
    for k in rows:
        group=ims[i:i+k]; i+=k
        ars=[im.width/im.height for im in group]
        h=(W-gap*(k-1))/sum(ars)
        canvas_rows.append((group,ars,h)); H+=h
    H=int(round(H+gap*(len(rows)-1)))
    c=Image.new('RGB',(W,H),(255,255,255)); y=0
    for group,ars,h in canvas_rows:
        x=0; hh=int(round(h))
        for j,(im,ar) in enumerate(zip(group,ars)):
            w=int(round(ar*h)) if j<len(group)-1 else W-x
            c.paste(ImageOps.fit(im,(w,hh),Image.LANCZOS),(x,y)); x+=w+gap
        y+=hh+gap
    c.save(out,quality=86,optimize=True,progressive=True)
    return c.size
if __name__=='__main__':
    print(collage(sys.argv[2:],sys.argv[1]))


def collage_fixed(paths, out, W=1600, aspect=4/3, gap=14, plan=None):
    """Collage at a fixed shape (default 4:3) so every news thumbnail matches.
    Tries every row arrangement (up to 3 photos per row) and keeps the one that needs the least
    cropping; crops favor keeping the top of each photo (heads)."""
    import itertools, math
    ims = [ImageOps.exif_transpose(Image.open(p)).convert('RGB') for p in paths]
    n = len(ims); H = round(W / aspect)
    def comps(k):
        if k == 0: yield []; return
        for f in (1, 2, 3):
            if f <= k:
                for r in comps(k - f): yield [f] + r
    best = None
    for rows in ([plan] if plan else comps(n)):
        i = 0; hs = []
        for k in rows:
            ars = [im.width / im.height for im in ims[i:i + k]]; i += k
            hs.append((W - gap * (k - 1)) / sum(ars))
        avail = H - gap * (len(rows) - 1)
        if avail <= 0: continue
        s = avail / sum(hs)
        # cost: how far cells are stretched from their natural shape, plus a penalty for very short rows
        cost = abs(math.log(s)) + sum(0.5 for h in hs if h * s < H * 0.22)
        if best is None or cost < best[0]: best = (cost, rows, [h * s for h in hs])
    _, rows, hs = best
    c = Image.new('RGB', (W, H), (255, 255, 255)); y = 0; i = 0
    for r, (k, h) in enumerate(zip(rows, hs)):
        hh = H - y if r == len(rows) - 1 else int(round(h))
        group = ims[i:i + k]; i += k
        ars = [im.width / im.height for im in group]; tot = sum(ars); x = 0
        for j, (im, ar) in enumerate(zip(group, ars)):
            w = int(round((W - gap * (k - 1)) * ar / tot)) if j < k - 1 else W - x
            c.paste(ImageOps.fit(im, (w, hh), Image.LANCZOS, centering=(0.5, 0.35)), (x, y)); x += w + gap
        y += hh + gap
    c.save(out, quality=86, optimize=True, progressive=True)
    return rows
