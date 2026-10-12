"""Render the daily Skai Reality quote / gyaan posts from daily/calendar.json.

Usage: python3 scripts/render_daily.py [YYYY-MM-DD ...]
Writes daily/out/<date>.jpg (1080x1350 JPEG) and daily/out/<date>.txt (full caption).
"""
import html
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CHROMIUM = "/opt/pw-browsers/chromium"
W, H = 1080, 1350

HASHTAGS = (
    "#SkaiReality #FractionYourFuture #RealEstateGyaan #RealEstateInvesting "
    "#PropertyInvestment #Bhiwandi #NaviMumbai #MumbaiRealEstate #RealEstateIndia "
    "#InvestSmart #WealthCreation #FinancialFreedom #MoneyMindset #InvestmentTips"
)
CTA = "Follow @skai_reality_bhiwandi for daily real estate gyaan. Invest karna hai? DM \"INVEST\"."

CSS = """
:root { --navy:#001b39; --navy2:#03284f; --yellow:#faac01; --cyan:#0099c5; --paper:#f6f3ec; }
* { box-sizing:border-box; margin:0; padding:0; }
html,body { width:1080px; height:1350px; }
body { font-family:Poppins, sans-serif; font-variant-numeric:lining-nums; }
.post { position:relative; width:1080px; height:1350px; overflow:hidden; display:flex; flex-direction:column; padding:90px 84px 80px; }
.hl { color:var(--yellow); }
.top { display:flex; align-items:center; justify-content:space-between; }
.logo { display:flex; align-items:center; gap:18px; }
.logo img { height:78px; }
.logo span { font-weight:600; font-size:30px; letter-spacing:.12em; }
.chip { font-size:22px; font-weight:600; letter-spacing:.18em; text-transform:uppercase; padding:12px 22px; border-radius:999px; }
.foot { margin-top:auto; display:flex; align-items:center; justify-content:space-between; font-size:24px; font-weight:500; letter-spacing:.04em; position:relative; z-index:2; }
.foot .line { flex:1; height:2px; margin:0 26px; }

/* motivation */
.mot { color:#fff; background:
   radial-gradient(900px 700px at 50% 30%, rgba(0,153,197,.22), transparent 65%),
   linear-gradient(180deg, var(--navy2), var(--navy) 70%); }
.mot .chip { color:var(--yellow); border:2px solid rgba(250,172,1,.6); }
.mot .mid { flex:1; display:flex; flex-direction:column; justify-content:center; padding-bottom:230px; position:relative; z-index:2; }
.mot .quote-mark { width:96px; height:14px; background:var(--yellow); border-radius:8px; }
.mot .q { font-weight:800; text-transform:uppercase; line-height:1.1; letter-spacing:-.005em; margin-top:40px; }
.mot .author { margin-top:36px; font-size:34px; color:#cfe3f0; font-weight:500; }
.mot .foot { color:#cfe3f0; } .mot .foot .line { background:rgba(255,255,255,.25); }
.skyline { position:absolute; left:0; right:0; bottom:0; height:420px; opacity:.45; z-index:1; }

/* gyaan */
.gy { background:var(--paper); color:var(--navy); }
.gy .hl { color:var(--cyan); }
.gy .logo span { color:var(--navy); }
.gy .chip { background:var(--navy); color:var(--yellow); }
.gy h1 { font-weight:800; font-size:76px; line-height:1.08; margin-top:70px; text-transform:uppercase; letter-spacing:-.01em; }
.gy .bar { width:120px; height:10px; background:var(--yellow); border-radius:6px; margin-top:34px; }
.gy .pts { margin-top:56px; display:flex; flex-direction:column; gap:38px; }
.gy .pt { display:grid; grid-template-columns:70px 1fr; gap:24px; align-items:start; }
.gy .n { width:70px; height:70px; border-radius:50%; background:var(--navy); color:var(--yellow); display:grid; place-items:center; font-weight:700; font-size:32px; }
.gy .pt h3 { font-size:40px; font-weight:700; line-height:1.2; }
.gy .pt p { font-size:31px; line-height:1.4; color:#33475e; margin-top:6px; font-weight:400; }
.gy .foot { color:var(--navy); } .gy .foot .line { background:rgba(0,27,57,.2); }
/* legend (photo + quote) */
.leg { background:var(--navy); color:#fff; }
.leg .photo { position:absolute; left:0; right:0; top:0; height:980px; background-size:cover; background-position:center 18%; }
.leg .shade { position:absolute; left:0; right:0; top:0; height:1350px;
   background:linear-gradient(180deg, rgba(0,27,57,.55) 0%, rgba(0,27,57,0) 18%, rgba(0,27,57,0) 38%, rgba(0,27,57,.85) 58%, var(--navy) 68%); }
.leg .top, .leg .lq, .leg .foot { position:relative; z-index:2; }
.leg .chip { color:var(--navy); background:var(--yellow); }
.leg .lq { margin-top:auto; padding-bottom:44px; }
.leg .mark { font-family:'Playfair Display', serif; font-weight:700; font-size:190px; line-height:.6; color:var(--yellow); height:84px; }
.leg .qt { font-weight:700; line-height:1.22; margin-top:18px; }
.leg .who { margin-top:30px; display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
.leg .who b { color:var(--yellow); font-size:36px; font-weight:700; }
.leg .who span { color:#b7c8da; font-size:26px; }
.leg .credit { position:absolute; right:84px; top:182px; z-index:2; font-size:15px; color:rgba(255,255,255,.55); }
.leg .foot { color:#cfe3f0; margin-top:0; } .leg .foot .line { background:rgba(255,255,255,.25); }
"""

SKYLINE = """
<svg class="skyline" viewBox="0 0 1080 520" preserveAspectRatio="none" aria-hidden="true">
 <defs><linearGradient id="sk" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#0099c5" stop-opacity=".9"/><stop offset="1" stop-color="#001b39" stop-opacity="0"/></linearGradient></defs>
 <g fill="url(#sk)">
  <rect x="0" y="330" width="80" height="190"/><rect x="88" y="250" width="70" height="270"/><rect x="166" y="300" width="96" height="220"/>
  <rect x="270" y="190" width="64" height="330"/><rect x="342" y="280" width="110" height="240"/><rect x="460" y="230" width="72" height="290"/>
  <rect x="540" y="140" width="84" height="380"/><rect x="632" y="260" width="104" height="260"/><rect x="744" y="200" width="70" height="320"/>
  <rect x="822" y="300" width="96" height="220"/><rect x="926" y="240" width="72" height="280"/><rect x="1006" y="320" width="74" height="200"/>
 </g>
 <g stroke="#faac01" stroke-width="4" fill="none" opacity=".7">
  <path d="M582 140 V70 M500 70 H760 M582 70 L540 140 M582 70 L624 140 M740 70 V118"/><rect x="730" y="118" width="20" height="16"/>
 </g>
</svg>
"""


def rich(text):
    """Escape text; *word* becomes a highlighted span; newlines become <br>."""
    out = html.escape(text)
    out = re.sub(r"\*(.+?)\*", r'<span class="hl">\1</span>', out)
    return out.replace("\n", "<br>")


def quote_size(text):
    longest = max(len(line) for line in text.replace("*", "").split("\n"))
    lines = text.count("\n") + 1
    size = min(124, int(912 / (max(longest, 8) * 0.7)))
    return min(size, int(700 / (lines * 1.1)))


def legend_size(quote):
    n = len(quote.replace("*", ""))
    return 64 if n <= 55 else 56 if n <= 80 else 48


def photo_info(post):
    credits = json.loads((ROOT / "photos" / "credits.json").read_text(encoding="utf-8"))
    info = credits[post["photo"]]
    return (ROOT / "photos" / info["file"]).as_uri(), info["credit"]


def page(post):
    variant = "skai-logo-icon-dark.png" if post["type"] == "gyaan" else "skai-logo-icon.png"
    logo_uri = (ROOT / "brand" / variant).as_uri()
    top = (f'<div class="top"><div class="logo"><img src="{logo_uri}"><span>SKAI REALITY</span></div>'
           f'<div class="chip">{html.escape(post["tag"])}</div></div>')
    foot = ('<div class="foot"><span>@skai_reality_bhiwandi</span><span class="line"></span>'
            '<span>Fraction Your Future</span></div>')
    if post["type"] == "legend":
        photo_uri, credit = photo_info(post)
        body = (f'<section class="post leg"><div class="photo" style="background-image:url(\'{photo_uri}\')"></div>'
                f'<div class="shade"></div><div class="credit">Photo: {html.escape(credit)}</div>{top}'
                f'<div class="lq"><div class="mark">“</div>'
                f'<div class="qt" style="font-size:{legend_size(post["quote"])}px">{rich(post["quote"])}</div>'
                f'<div class="who"><b>— {html.escape(post["person"])}</b><span>{html.escape(post["title"])}</span></div></div>'
                f'{foot}</section>')
    elif post["type"] == "motivation":
        author = f'<div class="author">— {html.escape(post["author"])}</div>' if post.get("author") else ""
        body = (f'<section class="post mot">{top}<div class="mid"><div class="quote-mark"></div>'
                f'<div class="q" style="font-size:{quote_size(post["text"])}px">{rich(post["text"])}</div>'
                f'{author}</div>{SKYLINE}{foot}</section>')
    else:
        pts = "".join(
            f'<div class="pt"><div class="n">{i}</div><div><h3>{html.escape(h)}</h3><p>{html.escape(p)}</p></div></div>'
            for i, (h, p) in enumerate(post["points"], 1))
        body = (f'<section class="post gy">{top}<h1>{rich(post["title"])}</h1><div class="bar"></div>'
                f'<div class="pts">{pts}</div>{foot}</section>')
    return ('<!doctype html><html><head><meta charset="utf-8">'
            '<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">'
            f'<style>{CSS}</style></head><body>{body}</body></html>')


def caption(post):
    if post["type"] == "legend":
        quote = post["quote"].replace("*", "")
        src = f' ({post["source"]})' if post.get("source") else ""
        _, credit = photo_info(post)
        tag = "#" + re.sub(r"[^A-Za-z]", "", post["person"])
        return (f'"{quote}"\n— {post["person"]}{src}\n\n{post["caption"]}\n\n{CTA}\n\n'
                f'Photo: {credit}\n\n{tag} {HASHTAGS}\n')
    return f'{post["caption"]}\n\n{CTA}\n\n{HASHTAGS}\n'


def render(post, out_dir):
    with tempfile.TemporaryDirectory() as tmp:
        src, shot = Path(tmp) / "p.html", Path(tmp) / "p.png"
        src.write_text(page(post), encoding="utf-8")
        subprocess.run([CHROMIUM, "--headless", "--no-sandbox", "--hide-scrollbars", "--allow-file-access-from-files",
                        "--virtual-time-budget=8000", f"--window-size={W},{H + 250}", f"--screenshot={shot}", src.as_uri()],
                       check=True, capture_output=True, timeout=90)
        Image.open(shot).convert("RGB").crop((0, 0, W, H)).save(out_dir / f'{post["date"]}.jpg', quality=92)
    (out_dir / f'{post["date"]}.txt').write_text(caption(post), encoding="utf-8")


def main():
    posts = json.loads((ROOT / "daily" / "calendar.json").read_text(encoding="utf-8"))
    wanted = set(sys.argv[1:])
    out_dir = ROOT / "daily" / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    for post in posts:
        if not wanted or post["date"] in wanted:
            render(post, out_dir)
            print("rendered", post["date"], post["type"])


if __name__ == "__main__":
    main()
