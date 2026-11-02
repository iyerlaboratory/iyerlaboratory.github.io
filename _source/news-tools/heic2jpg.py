import struct, sys, ctypes, numpy as np
from PIL import Image
def boxes(b, off, end):
    while off < end:
        size, typ = struct.unpack('>I4s', b[off:off+8]); hdr=8
        if size==1: size=struct.unpack('>Q',b[off+8:off+16])[0]; hdr=16
        elif size==0: size=end-off
        yield typ.decode('latin1'), off+hdr, off+size
        off += size
def find(b, off, end, typ):
    for t,s,e in boxes(b,off,end):
        if t==typ: return s,e
data=open(sys.argv[1],'rb').read()
ms,me=find(data,0,len(data),'meta'); ms+=4
# pitm
ps,pe=find(data,ms,me,'pitm'); ver=data[ps]; primary=struct.unpack('>H' if ver==0 else '>I', data[ps+4:ps+6] if ver==0 else data[ps+4:ps+8])[0]
# iinf
infos={}
s,e=find(data,ms,me,'iinf'); ver=data[s]; p=s+4; p+= 2 if ver==0 else 4
for t,bs,be in boxes(data,p,e):
    v=data[bs]; q=bs+4
    if v>=2:
        iid=struct.unpack('>H' if v==2 else '>I',data[q:q+(2 if v==2 else 4)])[0]; q+= 2 if v==2 else 4
        q+=2; typ=data[q:q+4].decode(); infos[iid]=typ
# iloc
s,e=find(data,ms,me,'iloc'); ver=data[s]; p=s+4
a,bb=data[p],data[p+1]; osz,lsz,bsz=a>>4,a&15,bb>>4; isz = bb&15 if ver in (1,2) else 0; p+=2
def rd(n):
    global p
    v=int.from_bytes(data[p:p+n],'big') if n else 0; p+=n; return v
cnt=rd(2 if ver<2 else 4); loc={}
for _ in range(cnt):
    iid=rd(2 if ver<2 else 4)
    cm = rd(2)&15 if ver in (1,2) else 0
    rd(2); base=rd(bsz); ec=rd(2); exts=[]
    for _ in range(ec):
        if ver in (1,2) and isz: rd(isz)
        eo=rd(osz); el=rd(lsz); exts.append((base+eo,el))
    loc[iid]=(cm,exts)
_idat=find(data,ms,me,'idat')
def itemdata(i):
    cm,exts=loc[i]
    if cm==1: return b''.join(data[_idat[0]+o:_idat[0]+o+l] for o,l in exts)
    return b''.join(data[o:o+l] for o,l in exts)
# iref
refs={}
r=find(data,ms,me,'iref')
if r:
    s,e=r; ver=data[s]; p=s+4
    for t,bs,be in boxes(data,p,e):
        q=bs; n=2 if ver==0 else 4
        fr=int.from_bytes(data[q:q+n],'big'); q+=n; c=struct.unpack('>H',data[q:q+2])[0]; q+=2
        to=[int.from_bytes(data[q+k*n:q+(k+1)*n],'big') for k in range(c)]; refs.setdefault((t,fr),[]).extend(to)
# iprp
s,e=find(data,ms,me,'iprp'); cs,ce=find(data,s,e,'ipco')
props=[(t,bs,be) for t,bs,be in boxes(data,cs,ce)]
assoc={}
for t,bs,be in boxes(data,s,e):
    if t=='ipma':
        ver=data[bs]; fl=int.from_bytes(data[bs+1:bs+4],'big'); q=bs+4; n=struct.unpack('>I',data[q:q+4])[0]; q+=4
        for _ in range(n):
            iid=int.from_bytes(data[q:q+(2 if ver<1 else 4)],'big'); q+= 2 if ver<1 else 4
            c=data[q]; q+=1; L=[]
            for _ in range(c):
                if fl&1: v=struct.unpack('>H',data[q:q+2])[0]; q+=2; idx=v&0x7fff
                else: idx=data[q]&0x7f; q+=1
                L.append(idx-1)
            assoc[iid]=L
def prop(i,typ):
    for k in assoc.get(i,[]):
        if props[k][0]==typ: return props[k]
lib=ctypes.CDLL('libde265.so.0')
lib.de265_new_decoder.restype=ctypes.c_void_p
lib.de265_get_next_picture.restype=ctypes.c_void_p
lib.de265_get_image_plane.restype=ctypes.POINTER(ctypes.c_uint8)
def decode(i):
    t,bs,be=prop(i,'hvcC'); h=data[bs:be]; q=22; n=h[q]; q+=1; nals=[]
    for _ in range(n):
        q+=1; c=struct.unpack('>H',h[q:q+2])[0]; q+=2
        for _ in range(c):
            l=struct.unpack('>H',h[q:q+2])[0]; q+=2; nals.append(h[q:q+l]); q+=l
    ls=(h[21]&3)+1; d=itemdata(i); q=0
    while q<len(d):
        l=int.from_bytes(d[q:q+ls],'big'); q+=ls; nals.append(d[q:q+l]); q+=l
    ctx=lib.de265_new_decoder(ctypes.c_void_p())
    lib.de265_new_decoder.argtypes=[]
    for nal in nals:
        buf=ctypes.create_string_buffer(nal,len(nal))
        lib.de265_push_NAL(ctypes.c_void_p(ctx),buf,len(nal),ctypes.c_longlong(0),ctypes.c_void_p())
    lib.de265_flush_data(ctypes.c_void_p(ctx))
    more=ctypes.c_int(1)
    img=None
    for _ in range(10000):
        err=lib.de265_decode(ctypes.c_void_p(ctx),ctypes.byref(more))
        img=lib.de265_get_next_picture(ctypes.c_void_p(ctx))
        if img or not more.value or (err!=0 and err<1000): break
    if not img: raise SystemExit('decode failed err=%d'%err)
    planes=[]
    for c in range(3):
        st=ctypes.c_int()
        ptr=lib.de265_get_image_plane(ctypes.c_void_p(img),c,ctypes.byref(st))
        w=lib.de265_get_image_width(ctypes.c_void_p(img),c); hh=lib.de265_get_image_height(ctypes.c_void_p(img),c)
        a=np.ctypeslib.as_array(ptr,shape=(hh*st.value,)).reshape(hh,st.value)[:,:w].copy(); planes.append(a)
    return planes
def full_range(i):
    r=prop(i,'colr')
    if r:
        t,bs,be=r
        if data[bs:bs+4]==b'nclx': return bool(data[bs+10]&0x80)
    return True
def toimg(i):
    if infos[i]=='grid':
        d=itemdata(i); fl=d[1]; rows,cols=d[2]+1,d[3]+1; n=4 if fl&1 else 2
        W=int.from_bytes(d[4:4+n],'big'); H=int.from_bytes(d[4+n:4+2*n],'big')
        tiles=refs[('dimg',i)]; Y=U=V=None
        for k,tid in enumerate(tiles):
            y,u,v=decode(tid); th,tw=y.shape
            if Y is None:
                Y=np.zeros((rows*th,cols*tw),np.uint8); U=np.zeros((rows*u.shape[0],cols*u.shape[1]),np.uint8); V=U.copy()
            r,c=divmod(k,cols)
            Y[r*th:(r+1)*th,c*tw:(c+1)*tw]=y; U[r*u.shape[0]:(r+1)*u.shape[0],c*u.shape[1]:(c+1)*u.shape[1]]=u; V[r*u.shape[0]:(r+1)*u.shape[0],c*u.shape[1]:(c+1)*u.shape[1]]=v
        fr=full_range(tiles[0]) if prop(i,'colr') is None else full_range(i)
    else:
        Y,U,V=decode(i); W,H=Y.shape[1],Y.shape[0]; fr=full_range(i)
    sy=Y.shape[0]//U.shape[0]; sx=Y.shape[1]//U.shape[1]
    U=U.repeat(sy,0).repeat(sx,1)[:Y.shape[0],:Y.shape[1]].astype(np.float32)-128; V=V.repeat(sy,0).repeat(sx,1)[:Y.shape[0],:Y.shape[1]].astype(np.float32)-128
    y=Y.astype(np.float32)
    if not fr: y=(y-16)*255/219; U*=255/224; V*=255/224
    R=y+1.402*V; G=y-0.344136*U-0.714136*V; B=y+1.772*U
    rgb=np.clip(np.stack([R,G,B],-1),0,255).astype(np.uint8)[:H,:W]
    im=Image.fromarray(rgb)
    r=prop(i,'irot')
    if r:
        ang=(data[r[1]]&3)*90
        if ang: im=im.rotate(ang,expand=True)
    m=prop(i,'imir')
    if m: im=im.transpose(Image.FLIP_LEFT_RIGHT if data[m[1]]&1 else Image.FLIP_TOP_BOTTOM)
    return im
im=toimg(primary); print(im.size, 'fullrange?'); im.save(sys.argv[2],quality=92)
