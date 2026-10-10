import sys; sys.path.insert(0,'/root/funny')
from kit import *
from playwright.sync_api import sync_playwright
def shot(html,ids):
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page(viewport={'width':430,'height':860},device_scale_factor=2)
        pg.goto('file:///root/funny/b/'+html); pg.wait_for_timeout(300); pg.screenshot(path=html+'.png',full_page=True)
        r={i:pg.eval_on_selector('#'+i,'e=>{const b=e.getBoundingClientRect();return [b.x,b.y+scrollY,b.width,b.height]}') for i in ids}
        b.close()
    im=Image.open(html+'.png').convert('RGB'); s=700/im.width*2  # css px -> phone px (im is 2x)
    return fit_width(im), {k:[v*700/430 for v in r[k]] for k in r}
bad,br=shot('bad.html',['title','uc','music','counter','phone'])
good,gr=shot('good.html',['h','cta'])
V='am_michael'
L=[(V,"Let's roast this website.",0.2),(V,"Comic Sans. In twenty twenty six. Bold choice.",0),
   (V,"Under construction since twenty nineteen. Take your time, bro.",0),
   (V,"Autoplay music. Nobody asked for the jingle.",0),
   (V,"Visitor number seven. That's the owner's mum.",0),
   (V,"And the phone number? Yellow, on white, hiding in the footer.",0.2),
   (V,"Here's the ten second fix.",0),(V,"One clear headline. One big call button. Done.",0.3),
   (V,"Rate the old one out of ten in the comments. Follow for more.",0)]
tl,dur=voice(L,'v.wav'); dur+=0.4
HL={1:'title',2:'uc',3:'music',4:'counter',5:'phone'}
bg=background(1)
def cur(t):
    c=None
    for s,e,i in tl:
        if t>=s-0.05: c=i
    return c
def frame(t):
    im=bg.copy(); d=ImageDraw.Draw(im); i=cur(t) or 0
    if i>=8 and t>=tl[8][0]:
        end_card(im,0,t); caption(d,L[8][1],y=1300,keys=("comments",)); return im
    if i<=5:
        page,rects=bad,br; pill(d,'ROAST THIS WEBSITE',150,(239,68,68))
        sc=0
        if i in HL:
            x,y,w,h=rects[HL[i]]; target=max(0,min(page.height-1180,int(y-400))); sc=target
            # smooth scroll from previous target
            prev=HL.get(i-1); 
            if prev:
                py=max(0,min(page.height-1180,int(rects[prev][1]-400))); a=ease((t-tl[i][0])/0.5); sc=int(py+(target-py)*a)
        phone(im,page,sc)
        if i in HL:
            x,y,w,h=rects[HL[i]]; X,Y=190+x-8,250+y-sc-8
            if 250<Y<1430: d.rounded_rectangle([X,Y,X+w+16,Y+h+16],radius=14,outline=YEL,width=8)
    else:
        page,rects=good,gr; pill(d,'FIXED',150,(34,197,94)); phone(im,page,0)
        if i==7:
            for k in ('h','cta'):
                x,y,w,h=rects[k]; d.rounded_rectangle([190+x-8,250+y-8,190+x+w+8,250+y+h+8],radius=14,outline=YEL,width=8)
    caption(d,L[i][1],keys=("comic","sans","jingle","mum","footer","fix","done","seven","construction"))
    return im
render(frame,dur,'v.wav','short.mp4','.')
contact('short.mp4',[3,8,13,17,24,27],'chk.png',w=240)
print(dur)
