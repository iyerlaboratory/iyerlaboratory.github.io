import cv2, numpy as np, sys
src,out=sys.argv[1],sys.argv[2]
im=cv2.imread(src).astype(np.float32)
# kill vertical screen-pixel stripes: smooth along x only
k=cv2.getGaussianKernel(9,1.8).T
d=cv2.filter2D(im,-1,k)
d=cv2.bilateralFilter(d,7,18,5)
b=cv2.GaussianBlur(d,(0,0),2.5); b2=cv2.GaussianBlur(d,(0,0),6)
s=d+0.9*(d-b)+0.35*(d-b2)
s=np.clip(s,0,255).astype(np.uint8)
lab=cv2.cvtColor(s,cv2.COLOR_BGR2LAB)
cl=cv2.createCLAHE(clipLimit=1.4,tileGridSize=(8,8))
lab[...,0]=cv2.addWeighted(cl.apply(lab[...,0]),0.5,lab[...,0],0.5,0)
cv2.imwrite(out,cv2.cvtColor(lab,cv2.COLOR_LAB2BGR),[cv2.IMWRITE_JPEG_QUALITY,93])
