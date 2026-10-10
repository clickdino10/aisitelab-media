import sys; sys.path.insert(0,'/root/funny')
from kit import *
C,D='af_nicole','am_michael'
L=[(C,"Hi! Can you make my website pop?",0),(D,"Sure. What do you mean by pop?",0),
   (C,"You know. Pop. But also minimal.",0),(D,"Okay. Pop, but minimal.",0.2),
   (C,"And make the logo bigger.",0),(D,"It's already half the screen.",0),
   (C,"Bigger.",0.3),(D,"Done.",0.6),(C,"Perfect! Now make it smaller.",0.6),(D,"",0.4),(D,"Tag a designer who needs a holiday. Follow for more.",0)]
SHOW=["Hi! Can you make my website pop?","Sure. What do you mean by \"pop\"?","You know. Pop. But also minimal.","Okay. Pop, but minimal.",
      "And make the logo bigger.","It's already half the screen.","Bigger.","[IMG]","Perfect! Now make it smaller.","..."]
tl,dur=voice(L,'v.wav'); dur+=0.4
bg=background(0)
# giant-logo website image
def giant():
    im=Image.new('RGB',(440,330),'white'); d=ImageDraw.Draw(im)
    d.rectangle([0,0,440,330],fill=(254,243,199))
    f=font(150); t="KEDAI"; d.text(((440-d.textlength(t,font=f))/2,40),t,font=f,fill=(220,38,38))
    d.text((150,240),"Welcome to our sh...",font=font(18,False),fill=(120,53,15))
    return im
G=giant(); SW,SH=700,1180
fm=font(40,False); fn=font(30)
def wrap(d,t,maxw):
    out=[];cur=''
    for w in t.split():
        tt=(cur+' '+w).strip()
        if d.textlength(tt,font=fm)>maxw and cur: out.append(cur);cur=w
        else: cur=tt
    out.append(cur); return out
def chat(t):
    s=Image.new('RGB',(SW,SH),(241,245,249)); d=ImageDraw.Draw(s)
    items=[]
    for i,msg in enumerate(SHOW):
        st=tl[i][0]-0.1
        if t<st-0.5: break
        mine=(L[i][0]==D)
        typing=t<st
        items.append((msg,mine,typing,st))
    # layout bottom-up
    blocks=[]
    for msg,mine,typing,st in items:
        if typing: h=80; blocks.append(('typing',mine,h,None)); continue
        if msg=='[IMG]': blocks.append(('img',mine,G.height+30,None)); continue
        lines=wrap(d,msg,470); h=len(lines)*54+44; blocks.append(('txt',mine,h,lines))
    total=sum(b[2]+18 for b in blocks); top=170; avail=SH-top-40
    y=top-max(0,total-avail)
    for kind,mine,h,lines in blocks:
        if kind=='typing':
            x=SW-200 if mine else 30
            d.rounded_rectangle([x,y,x+170,y+h-10],radius=30,fill=(59,130,246) if mine else 'white')
            for k in range(3):
                ph=(t*3+k*0.3)%1; r=9+4*(ph<0.5)
                cx=x+50+k*35; cy=y+35; d.ellipse([cx-r,cy-r,cx+r,cy+r],fill='white' if mine else (148,163,184))
        elif kind=='img':
            x=SW-G.width-40; d.rounded_rectangle([x-12,y,x+G.width+12,y+h],radius=24,fill=(59,130,246)); s.paste(G,(x,y+15))
        else:
            wmax=max(d.textlength(l,font=fm) for l in lines)+50
            x=SW-wmax-30 if mine else 30
            d.rounded_rectangle([x,y,x+wmax,y+h],radius=30,fill=(59,130,246) if mine else 'white')
            ty=y+18
            for l in lines: d.text((x+25,ty),l,font=fm,fill='white' if mine else (15,23,42)); ty+=54
        y+=h+18
    d.rectangle([0,0,SW,150],fill='white'); d.ellipse([30,62,100,132],fill=(251,146,60))
    d.text((52,74),"C",font=font(40),fill='white'); d.text((120,70),"Client",font=fn,fill=(15,23,42))
    d.text((120,106),"online",font=font(22,False),fill=(34,197,94)); d.line([0,150,SW,150],fill=(226,232,240),width=2)
    return s
END=tl[10][0]
def frame(t):
    im=bg.copy(); d=ImageDraw.Draw(im)
    if t>=END-0.1:
        end_card(im,END,t); caption(d,"Tag a designer who needs a holiday",y=1300,keys=("designer",)); return im
    pill(d,'When the client says "make it pop"',150,(239,68,68),size=38)
    phone(im,chat(t))
    return im
render(frame,dur,'v.wav','short.mp4','.')
contact('short.mp4',[2,9,15,19.5,dur-1],'chk.png')
print(dur)
