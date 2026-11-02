import cv2, numpy as np, sys
from PIL import Image, ImageOps
src, out = sys.argv[1], sys.argv[2]
im = np.array(ImageOps.exif_transpose(Image.open(src)).convert('RGB')).astype(np.float32)/255
H,W = im.shape[:2]; s = W/2576
# 1) remove veiling glare/flare: smooth "floor" of the image, subtracted strongly
dark = cv2.erode(im.min(axis=2), cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(int(31*s)|1,)*2))
veil = cv2.GaussianBlur(dark,(0,0),45*s)
# only treat glare above the scene's base black level
base = np.percentile(veil, 5)
v = np.clip(veil-base,0,None)[...,None]*0.95
J = np.clip((im - v)/np.clip(1-v,0.3,1),0,1)
# remove colored flare tint: where glare is strong, pull chroma toward local neutral
lab = cv2.cvtColor((J*255).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
g = np.clip(v[...,0]/0.25,0,1)
for c in (1,2): lab[...,c] = 128 + (lab[...,c]-128)*(1-0.45*g)
# 2) backlight compensation: local tone mapping on L (compress big bright areas, lift shadows)
L = lab[...,0]/255
logL = np.log(L+0.02)
basel = cv2.bilateralFilter(logL.astype(np.float32), int(25*s)|1, 0.4, 30*s)
detail = logL - basel
target = np.log(0.50)
basel2 = target + (basel - target)*0.55
Ln = np.exp(basel2 + detail*1.15) - 0.02
Ln = np.clip(Ln,0,1)
lab[...,0] = Ln*255
J = cv2.cvtColor(np.clip(lab,0,255).astype(np.uint8), cv2.COLOR_LAB2RGB).astype(np.float32)/255
# gentle contrast + saturation recovery
lo,hi = np.percentile(J,0.5),np.percentile(J,99.7)
J = np.clip((J-lo)/(hi-lo),0,1)
# shadow/midtone lift for faces, then S-curve for punch
J = J**0.75
J = np.clip(J + 0.12*np.sin(np.pi*J)*(J-0.35),0,1)
J[...,0]*=1.03; J[...,2]*=0.97; J=np.clip(J,0,1)
hsv = cv2.cvtColor((J*255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
hsv[...,1] = np.clip(hsv[...,1]*1.15,0,255)
J = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
o = Image.fromarray(J); o = o.crop((0,int(180*s),o.width,o.height)); o.save(out, quality=95)
