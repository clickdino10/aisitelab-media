"""Shared toolkit for AI Site Lab funny Shorts: voice, frames, captions, encode."""
import json, os, subprocess
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_B = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FONT_M = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
EMOJI = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, H, FPS = 1080, 1920, 30
NAVY = (11, 15, 26); CYAN = (34, 211, 238); VIO = (139, 92, 246); YEL = (250, 204, 21)
SR = 24000
_k = None


def font(size, bold=True):
    return ImageFont.truetype(FONT_B if bold else FONT_M, size)


def voice(lines, out_wav, speed=1.05, lead=0.3, gap=0.25):
    """lines: list of (voice, text, extra_pause). Returns timeline [(start,end,idx)]."""
    global _k
    from kokoro_onnx import Kokoro
    if _k is None:
        _k = Kokoro("/root/tts/kokoro.onnx", "/root/tts/voices.bin")
    parts = [np.zeros(int(lead * SR), np.float32)]; t = lead; tl = []
    for i, (v, text, pause) in enumerate(lines):
        if text:
            a, _ = _k.create(text, voice=v, speed=speed, lang="en-us")
            a = a.astype(np.float32)
        else:
            a = np.zeros(int(0.6 * SR), np.float32)
        tl.append((t, t + len(a) / SR, i)); parts.append(a); t += len(a) / SR
        g = gap + (pause or 0); parts.append(np.zeros(int(g * SR), np.float32)); t += g
    sf.write(out_wav, np.concatenate(parts), SR)
    return tl, t


def background(seed=0):
    bg = Image.new("RGB", (W, H), NAVY)
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(gl)
    if seed % 2 == 0:
        d.ellipse([-200, 300, 700, 1200], fill=VIO + (110,)); d.ellipse([500, 800, 1300, 1700], fill=CYAN + (90,))
    else:
        d.ellipse([400, 100, 1300, 1000], fill=VIO + (110,)); d.ellipse([-300, 900, 600, 1800], fill=CYAN + (90,))
    gl = gl.filter(ImageFilter.GaussianBlur(170)); bg.paste(gl, (0, 0), gl)
    d = ImageDraw.Draw(bg); f = font(34); t = "AI SITE LAB"
    d.text(((W - d.textlength(t, font=f)) / 2, 70), t, font=f, fill=CYAN)
    return bg


def pill(d, text, y, fill, fg="white", size=40):
    f = font(size); tw = d.textlength(text, font=f); x = (W - tw - 48) / 2
    d.rounded_rectangle([x, y, x + tw + 48, y + size + 26], radius=(size + 26) // 2, fill=fill)
    d.text((x + 24, y + 6), text, font=f, fill=fg)


def caption(d, text, y=1490, keys=(), size=64, maxw=940):
    f = font(size); words = text.split(); lines = []; cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > maxw and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    lines.append(cur)
    for ln in lines:
        x = (W - d.textlength(ln, font=f)) / 2
        for w in ln.split(" "):
            bare = w.strip(".,!?:;'\"").lower()
            hit = any(bare == k.lower() for k in keys)
            d.text((x, y), w, font=f, fill=YEL if hit else (255, 255, 255), stroke_width=7, stroke_fill=(0, 0, 0))
            x += d.textlength(w + " ", font=f)
        y += int(size * 1.28)


def phone(im, screen, scroll=0, x=190, y=250, sw=700, sh=1180):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([x - 18, y - 18, x + sw + 18, y + sh + 18], radius=70, fill=(30, 41, 59), outline=(71, 85, 105), width=4)
    crop = screen.crop((0, scroll, sw, scroll + sh))
    m = Image.new("L", (sw, sh), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, sw - 1, sh - 1], radius=54, fill=255)
    im.paste(crop, (x, y), m)
    d.rounded_rectangle([x + sw // 2 - 70, y + 14, x + sw // 2 + 70, y + 38], radius=12, fill=(15, 23, 42))


def fit_width(img, w=700):
    return img.resize((w, int(img.height * w / img.width)))


def screenshot(html_path, out_png, width=430, height=860, full=True):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": width, "height": height}, device_scale_factor=2)
        pg.goto("file://" + os.path.abspath(html_path)); pg.wait_for_timeout(300)
        pg.screenshot(path=out_png, full_page=full); b.close()
    return Image.open(out_png).convert("RGB")


def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


def end_card(im, t0, t):
    d = ImageDraw.Draw(im)
    f1 = font(110); s = "AI Site Lab"; d.text(((W - d.textlength(s, font=f1)) / 2, 720), s, font=f1, fill="white")
    f3 = font(48); s = "Build websites with AI"; d.text(((W - d.textlength(s, font=f3)) / 2, 870), s, font=f3, fill=(148, 163, 184))
    d.rounded_rectangle([290, 1000, 790, 1100], radius=50, fill=CYAN); s = "FOLLOW"
    d.text(((W - d.textlength(s, font=f3)) / 2, 1018), s, font=f3, fill=NAVY)


def render(frame_fn, dur, wav, out_mp4, workdir):
    fdir = os.path.join(workdir, "f"); os.makedirs(fdir, exist_ok=True)
    for f in os.listdir(fdir):
        os.remove(os.path.join(fdir, f))
    n = int(dur * FPS)
    for i in range(n):
        frame_fn(i / FPS).save(f"{fdir}/{i:05d}.jpg", quality=88)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", f"{fdir}/%05d.jpg", "-i", wav,
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "fast", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", out_mp4], check=True)


def contact(mp4, times, out_png, w=270):
    ims = []
    for i, s in enumerate(times):
        p = f"{out_png}.{i}.jpg"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(s), "-i", mp4, "-frames:v", "1", "-vf", f"scale={w}:-1", p], check=True)
        ims.append(Image.open(p))
    S = Image.new("RGB", (w * len(ims), ims[0].height))
    for i, im in enumerate(ims):
        S.paste(im, (i * w, 0))
    S.save(out_png)
