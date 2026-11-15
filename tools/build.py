"""Build static VARON TAILOR site. usage: python3 -I tools/build.py   (run from anywhere)
1) copy delivered assets ../assets/{images,videos}/<slot id>.* -> media/
2) make neutral placeholders for missing image slots
3) render all pages from the templates below
"""
import json, os, shutil, glob, html
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOB = os.path.dirname(SITE)
MI, MV = f"{SITE}/media/images", f"{SITE}/media/videos"
os.makedirs(MI, exist_ok=True); os.makedirs(MV, exist_ok=True)

SLOTS = json.load(open(f"{JOB}/audit/slots.json"))["slots"]
RATIO = {}
for s in SLOTS:
    if s.get("kind") in ("image", "video") and "/" not in s["id"]:
        w, h = s["size_px"]; RATIO[s["id"]] = (w, h)
        if s["kind"] == "video": RATIO[s["id"] + "-poster"] = (w, h)

def resolve(sid):
    """return media path for slot id (delivered file preferred, else placeholder)."""
    for ext in ("jpg", "jpeg", "png", "webp"):
        src = f"{JOB}/assets/images/{sid}.{ext}"
        if os.path.exists(src):
            dst = f"{MI}/{sid}.{ext}"
            if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst): shutil.copy2(src, dst)
            return f"media/images/{sid}.{ext}"
    ph = f"{MI}/{sid}.ph.jpg"
    if not os.path.exists(ph):
        from PIL import Image, ImageDraw
        w, h = RATIO.get(sid, (1200, 1800)); sc = 900 / max(w, h)
        im = Image.new("RGB", (max(1, int(w * sc)), max(1, int(h * sc))), (226, 223, 218))
        d = ImageDraw.Draw(im); d.text((12, 10), sid, fill=(150, 146, 140)); im.save(ph, quality=80)
    return f"media/images/{sid}.ph.jpg"

def video(sid):
    src = f"{JOB}/assets/videos/{sid}.mp4"
    if os.path.exists(src):
        dst = f"{MV}/{sid}.mp4"
        if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst): shutil.copy2(src, dst)
        return f"media/videos/{sid}.mp4"
    return ""

def img(sid, alt="", cls=""):
    return f'<img src="{resolve(sid)}" alt="{html.escape(alt)}"{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} loading="lazy">'

# ---------- brand facts (BRIEF.md 브랜드 사실) ----------
BR = "VARON TAILOR"; BR_KO = "바론테일러"
KAKAO = "https://open.kakao.com/o/stYrOg2b"; INSTA = "https://www.instagram.com/varon_tailor/"; THREADS = "https://www.threads.net/@varon_tailor"
STORES = [
    ("광주점", "Gwangju", "광주 동구 불로동 83-3 (광주웨딩거리 안 2층)", "062-225-7983"),
    ("순천점", "Suncheon", "전남 순천시 왕지로 2, 1층 (배스킨라빈스 옆)", "061-722-7983"),
]
NEED = "[확인 필요]"

PRODUCTS = ["Ivory Shawl Tuxedo", "Black Peak Lapel Tuxedo", "Charcoal Three-piece", "Navy Chalk Stripe 2-piece", "Grey Glen Check Suit",
            "Beige Double-breasted Suit", "Midnight Velvet Jacket", "Black Houndstooth 2-piece", "Steel Blue Suit", "Mocha Brown Suit",
            "Ivory Tweed Jacket", "Olive Herringbone Suit", "Light Grey Flannel Suit", "Navy Double-breasted Suit", "Black Mandarin Jacket",
            "Taupe Linen Suit", "Cream Morning Coat", "Dark Green Suit", "Graphite Sharkskin Suit", "White Dinner Jacket"]

def logo(size=None):
    st = f' style="font-size:{size}px"' if size else ""
    return f'<span class="logo-txt"{st}>{BR}</span>'

ARROW_L = '<svg viewBox="0 0 24 24"><path d="M22 12H2M8 6l-6 6 6 6"/></svg>'
ARROW_R = '<svg viewBox="0 0 24 24"><path d="M2 12h20M16 6l6 6-6 6"/></svg>'

MENU = [
    ("cate-logo", "index.html", None, [("About", "about.html"), ("Bespoke", "bespoke.html"), ("M.T.M", "mtm.html")]),
    ("", "wedding.html", "WEDDING LINE", []),
    ("", "archive.html", "ARCHIVE", []),
    ("", "#none", "COMMUNITY", [("Review", "review.html"), ("Lookbook", "lookbook.html"), ("Instagram", INSTA), ("Reservation", KAKAO)]),
    ("", "stores.html", "STORE", []),
]

def ext(href): return ' target="_blank" rel="noopener"' if href.startswith("http") else ""

def header():
    p = []
    for cls, href, label, sub in MENU:
        inner = logo(28) if cls == "cate-logo" else label
        s = "".join(f'<li class="cate_sub_li"><a href="{h}"{ext(h)}>{t}</a></li>' for t, h in sub)
        p.append(f'<li class="cate_li {cls}" data-m-mega-item><a href="{href}">{inner}</a>{f"<ul class=cate_sub data-m-mega-panel>{s}</ul>" if sub else ""}</li>')
    m = []
    for cls, href, label, sub in MENU:
        lab = f"{BR} BESPOKE" if cls == "cate-logo" else label
        s = "".join(f'<li><a href="{h}"{ext(h)}>{t}</a></li>' for t, h in sub)
        if sub:
            m.append(f'<li class="cate_li has-sub" data-m-acc-item><a href="{href}" data-m-acc-head>{lab}<span class="plus" data-m-acc-icon></span></a><ul class="cate_sub" data-m-acc-panel>{s}</ul></li>')
        else:
            m.append(f'<li class="cate_li"><a href="{href}">{lab}</a></li>')
    return f"""<header data-m-header>
 <div id="p-header"><nav class="header-top"><div id="p-main-menu"><ul class="prd_cate">{''.join(p)}</ul></div></nav><div class="header-top-bg" data-m-mega-bg></div></div>
 <div id="m-header"><nav class="header-bottom"><div class="nav-wrap" data-m-header-bar><div class="Logo"><a href="index.html">{logo(20)}</a></div><a href="#none" id="menu-open" class="menu-icon" data-m-menu-toggle aria-label="메뉴" aria-expanded="false"><span class="m-lines"><i></i><i></i><i></i></span></a></div>
  <aside id="m-main-menu" data-m-menu><div class="menulist"><nav data-m-acc="menu"><ul class="prd_cate">{''.join(m)}</ul></nav></div>
   <form class="m-search" action="shop-men.html"><input type="text" data-m-field placeholder="" aria-label="검색"></form></aside></nav></div>
</header>"""

def footer():
    stores = "".join(f"<span>{n} {a}</span><span>{n} {t}</span>" for n, _, a, t in STORES)
    return f"""<footer><div class="footer-top">
 <div class="box f-logo">{logo()}<span>{BR_KO} 맞춤정장 · 예복 · 비즈니스 수트</span><span>계좌·사업자번호 {NEED}</span><span>© {BR}. All rights reserved.</span></div>
 <div class="footer-accordion" data-m-acc="footer">
  <div class="box" data-m-acc-item><h2 data-m-acc-head>COMPANY<span class="chev" data-m-acc-icon></span></h2><ul class="accordion-content" data-m-acc-panel><li><a href="about.html">About</a></li><li><a href="stores.html">Store</a></li><li><a href="review.html">Review</a></li><li><a href="event.html">Event</a></li></ul></div>
  <div class="box" data-m-acc-item><h2 data-m-acc-head>HELP<span class="chev" data-m-acc-icon></span></h2><ul class="accordion-content" data-m-acc-panel><li><a href="notice.html">Notice</a></li><li><a href="qna.html">Q&amp;A</a></li><li><a href="guide.html">Guide</a></li></ul></div>
  <div class="box" data-m-acc-item><h2 data-m-acc-head>SOCIAL<span class="chev" data-m-acc-icon></span></h2><ul class="accordion-content" data-m-acc-panel><li><a href="{INSTA}" target="_blank" rel="noopener">Instagram</a></li><li><a href="{THREADS}" target="_blank" rel="noopener">Threads</a></li><li><a href="{KAKAO}" target="_blank" rel="noopener">상담 오픈채팅</a></li></ul></div>
  <div class="box contact" data-m-acc-item><h2 data-m-acc-head>CONTACT<span class="chev" data-m-acc-icon></span></h2><div class="accordion-content" data-m-acc-panel>{stores}</div></div>
 </div></div></footer>"""

def page(fname, title, body, main_cls="", extra_js=False, btt=True):
    vend = '<link rel="stylesheet" href="vendor/lenis.css">' + ('<link rel="stylesheet" href="vendor/swiper-bundle.min.css">' if extra_js else "")
    vjs = ('<script src="vendor/swiper-bundle.min.js"></script>' if extra_js else "")
    doc = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500&family=Cormorant+Garamond:wght@400;500&display=swap" rel="stylesheet">
{vend}<link rel="stylesheet" href="motion/motion.css"><link rel="stylesheet" href="css/style.css"></head>
<body><div id="pageOverlay" data-m-pagein aria-hidden="true"></div>
{header()}
<main class="layout-contents {main_cls}">
{body}
{'<div class="back-to-top" data-m-totop><a class="line-btn" href="#">Back to top</a></div>' if btt else ""}
</main>
{footer()}
<script src="vendor/lenis.min.js"></script>{vjs}<script src="motion/motion.js"></script><script src="js/main.js"></script>
</body></html>"""
    open(f"{SITE}/{fname}", "w").write(doc)

def card(i, name=True):
    n = f"{i:02d}"
    t = f'<div class="text-info"><div class="name">{PRODUCTS[i-1]}</div></div>' if name else ""
    return f'<a class="thumb-box" data-m-card-thumb href="detail.html">{img(f"prd-{n}-front", PRODUCTS[i-1])}<span class="thumb-back" data-m-card-back>{img(f"prd-{n}-back", "")}</span></a>{t}'

def bnr_pair(men_href, women_href):
    def one(sid, h, label, href):
        return f'<a href="{href}"><div class="img-box"><figure>{img(sid, label)}</figure></div><figcaption><h1>{label}</h1><small>Discover Looks</small></figcaption></a>'
    return one("home-men", "", "MEN", men_href) + one("home-women", "", "WOMEN", women_href)

# ---------------- pages ----------------
def build():
    vpc, vmo = video("home-hero-video-pc"), video("home-hero-video-mo")
    ppc, pmo = resolve("home-hero-video-pc-poster"), resolve("home-hero-video-mo-poster")
    lines = json.dumps(["창을 열고 커피를 내립니다.<br>여느 날과 같은 조용한 아침.", "거울 앞에서 단추를 하나씩 채웁니다.<br>오늘을 위해 맞춘 한 벌.",
                        "어깨선이 꼭 맞으면<br>걸음도 달라집니다."], ensure_ascii=False).replace('"', "&quot;")
    slides = "".join(f'<li class="swiper-slide item" data-m-card>{card(i, False)}</li>' for i in range(1, 21))
    home = f"""<div class="main-layout-contents-wrap">
<div class="main-bnr-wrap hero header-white" data-m-header-white><a href="wedding.html"><div class="img-box"><figure data-m-video>
 <video class="m-pc-only" autoplay muted loop playsinline poster="{ppc}" {f'src="{vpc}"' if vpc else ''}></video>
 <video class="m-mo-only" autoplay muted loop playsinline poster="{pmo}" {f'src="{vmo}"' if vmo else ''}></video>
 <p class="sub" data-lines="{lines}"></p></figure></div></a></div>
<div class="main-bnr-wrap header-white" data-m-header-white><a href="wedding.html" class="collection-band"><b>{BR} Collection</b><span>Tailored to the line of your shoulders, cut and finished by hand in our own workroom.<br>Made for the day you will remember.</span></a></div>
<div class="prd-slide-wrap" data-m-slider-wrap><div class="swiper" data-m-slider="free"><ul class="swiper-wrapper prdList-slide">{slides}</ul></div>
 <button class="nav prev" data-m-prev aria-label="이전">{ARROW_L}</button><button class="nav next" data-m-next aria-label="다음">{ARROW_R}</button></div>
<div class="main-bnr-wrap row header-white" data-m-header-white>{bnr_pair('shop-men.html', 'shop-women.html')}</div>
<div class="main-bnr-wrap header-white about-bnr" data-m-header-white><a href="about.html"><div class="img-box"><figure style="aspect-ratio:4320/2979">{img('home-about', 'ABOUT US')}</figure></div><figcaption><h1>ABOUT US</h1><small>View More</small></figcaption></a></div>
</div>"""
    page("index.html", f"{BR} | 예복·비즈니스 맞춤정장", home, "no-top is-home", True, btt=False)

    about = f"""<div id="about">
<section class="img-full pc-only"><figure>{img('about-hero', BR)}<span class="brand-over">VARON</span></figure><div style="height:154px"></div></section>
<section class="txt-row about-2"><figcaption><h1>ABOUT</h1>
<p>바론테일러는 옷을 파는 곳이기 전에 한 사람의 체형과 걸음을 읽는 곳입니다. 어깨의 기울기, 팔 길이의 차이, 서 있는 습관까지 직접 재고 기록합니다. 그렇게 쌓은 치수로 결혼식 날의 예복과 매일 입는 비즈니스 수트를 한 벌씩 따로 만듭니다. 광주와 순천, 두 매장의 재단사가 처음 상담부터 마지막 가봉까지 함께합니다. 몸에 맞는 옷은 설명이 필요 없다고 믿습니다.</p><br>
<p>Varon Tailor makes suits one person at a time. We measure the slope of your shoulders and the way you stand, then cut a pattern that belongs only to you, from the wedding day to every working day after.</p></figcaption>
<figure>{img('about-side', '')}</figure></section></div>"""
    page("about.html", f"About | {BR}", about)

    steps = [("상담", "원하시는 자리와 분위기, 평소 즐겨 입는 옷을 먼저 여쭙니다. 원단과 디자인은 그다음에 함께 고릅니다."),
             ("채촌", "목둘레부터 발목까지 서른 곳이 넘는 치수를 잽니다. 같은 사이즈라도 체형이 다르기 때문에 숫자 옆에 자세와 습관을 함께 적어 둡니다."),
             ("패턴 메이킹", "잰 치수와 기록을 바탕으로 재단사가 직접 종이 패턴을 그립니다. 기성 패턴을 고치는 방식이 아니라 처음부터 한 사람을 위한 선을 긋고, 한쪽 어깨가 낮다면 그 차이까지 패턴에 담습니다."),
             ("가봉", "임시로 꿰맨 옷을 입어 보며 어깨·허리·소매 길이를 다시 맞춥니다. 거울 앞에서 움직여 보고 불편한 곳을 바로 표시해 고칩니다."),
             ("완성", "가봉에서 고친 내용을 반영해 본봉제를 마칩니다. 마지막으로 다림질과 단추 위치를 확인한 뒤 고객님께 전해 드립니다.")]
    def li(i): return f'<li><h4><sup>{i+1}</sup>{steps[i][0]}</h4><p>{steps[i][1]}</p></li>'
    bespoke = f"""<div id="bespoke">
<section class="img-full bespoke"><figure>{img('bespoke-hero', '')}</figure></section>
<section class="txt-row"><figcaption><h1>BESPOKE</h1><h1>Full Handmade</h1><p>바론테일러의 비스포크는 재단부터 마무리까지 손으로 완성합니다.<br>한 벌을 만드는 데 필요한 시간을 줄이지 않습니다.</p></figcaption><figure></figure></section>
<section class="section-pad"><h1 style="margin-bottom:6.5px">PROCESS</h1><div class="process-wrap"><ul>{li(0)}{li(1)}{li(2)}</ul><ul>{li(3)}{li(4)}</ul></div></section></div>"""
    page("bespoke.html", f"Bespoke | {BR}", bespoke)

    items = [("mtm-item-1", "Jacket"), ("mtm-item-2", "Trouser"), ("mtm-item-3", "Over Coat")]
    mtm = f"""<div id="mtm">
<section class="mtm-1"><figure>{img('mtm-hero-1', '')}</figure><figure>{img('mtm-hero-2', '')}</figure></section>
<section class="txt-row"><figcaption style="max-width:none"><h1>M.T.M</h1><h1>Made to Measure</h1><p>일정이 촉박하거나 매장 방문이 어려운 분을 위해 M.T.M을 준비했습니다. 바론테일러가 쌓아 온 체형 기록과 기본 패턴 위에서<br>고객님의 치수만 정확히 옮겨 짧은 기간 안에 한 벌을 완성합니다.</p></figcaption></section>
<section class="mtm-3"><ul>{''.join(f'<li><a><figure>{img(s, t)}</figure><figcaption>{t}</figcaption></a></li>' for s, t in items)}</ul></section></div>"""
    page("mtm.html", f"M.T.M | {BR}", mtm)

    wedding = f"""<div id="wedding">
<section class="main-bnr-wrap row">{bnr_pair('shop-men.html', 'shop-women.html')}</section>
<section class="wedding-2"><figure>{img('rental-feature', '')}</figure><figcaption><h1>‘THE WEDDING LINE 2026’</h1><p>2026 WEDDING SUIT - 두 사람의 하루를 위한 예복.</p><a href="shop-men.html">DISCOVER THE PIECES</a></figcaption></section></div>"""
    page("wedding.html", f"Wedding Line | {BR}", wedding)

    def store_box(n, en, a, t):
        rows = [("매장주소", a), ("전화번호", f'<a href="tel:{t}">{t}</a>'), ("상담예약", f'<a href="{KAKAO}" target="_blank" rel="noopener">카카오 오픈채팅</a>'), ("영업시간", NEED)]
        r = "".join(f'<div class="sc-list-text"><span>{k}</span><span>{v}</span></div>' for k, v in rows)
        q = html.escape(a.split(" (")[0])
        return f"""<div class="sc-box"><div class="sc-title" data-m-sticky-title><h1>{BR} {en}</h1></div><div class="sc-list-wrapper"><div class="sc-list"><div class="sc-list-title"><h1>{n}({en})</h1></div>{r}</div></div></div>
<section class="store-map"><iframe title="{n} 지도" src="https://maps.google.com/maps?q={q}&output=embed"></iframe></section>"""
    stores = f"""<div id="stores"><div class="stores-content"><div class="stores-top"><figure>{img('stores-hero', '')}</figure></div>
{''.join(store_box(*s) for s in STORES)}</div></div>"""
    page("stores.html", f"Store | {BR}", stores)

    faq = [("상담 예약 안내", ["처음 방문하시는 분도 편하게 오실 수 있도록 상담은 예약 순서대로 한 분씩 진행합니다. 같은 시간에 여러 팀을 받지 않기 때문에 충분히 이야기를 나눌 수 있습니다.", "상담은 예약제로 운영합니다. 카카오 오픈채팅 또는 각 매장 전화로 원하시는 날짜와 매장을 알려 주세요.", "첫 상담은 약 1시간이 걸립니다. 평소 즐겨 입는 셔츠나 구두가 있으면 함께 가져오시면 좋습니다."]),
           ("제작 기간", ["비스포크는 가봉을 포함해 보통 4~6주가 걸립니다. 정확한 기간은 원단과 일정에 따라 달라지니 상담 때 함께 정합니다.", "M.T.M은 비스포크보다 짧은 기간에 완성됩니다. 예식 날짜가 정해져 있다면 상담 때 먼저 말씀해 주세요."]),
           ("가격 안내", [f"가격은 원단과 제작 방식에 따라 달라집니다. {NEED}"]),
           ("가봉과 수선", ["가봉은 1~2회 진행합니다. 완성 후에도 몸이 바뀌면 매장에서 다시 맞춰 드립니다.", "체중 조절 계획이 있으시면 마지막 가봉 일정을 그에 맞춰 잡는 것이 좋습니다.", "완성 후 처음 입어 보셨을 때 불편한 곳이 있으면 바로 말씀해 주세요. 소매 길이, 바지 기장, 허리 품은 매장에서 다시 손봐 드립니다.", "오래 입으신 수트의 단추 교체나 안감 수선도 상담해 드립니다."]),
           ("예복 준비", ["신랑 예복은 예식 2~3개월 전에 상담을 시작하시길 권합니다.", "혼주 정장과 들러리 정장도 함께 상담할 수 있습니다.", "본식과 2부 예복을 따로 준비하시는 경우, 두 벌의 색과 원단이 사진에서 어떻게 보일지 함께 비교해 드립니다.", "웨딩 촬영 일정이 본식보다 앞선다면 촬영 날짜에 맞춰 제작 순서를 조정합니다. 상담 때 촬영일을 꼭 알려 주세요.", "셔츠·타이·행커치프·구두 같은 소품도 수트에 맞춰 함께 골라 드립니다."]),
           ("결제 안내", [f"결제 방법과 환불 기준 {NEED}"]),
           ("원단 안내", ["사계절 울, 플란넬, 린넨, 벨벳 등 계절과 자리에 맞는 원단을 준비해 두고 있습니다. 같은 네이비라도 결과 광택이 달라 사진에서 보이는 느낌이 다르므로, 매장 조명과 창가 빛에서 함께 비교해 보시길 권합니다.", "예복은 실내 예식장 조명에서 은은하게 빛나는 원단을, 비즈니스 수트는 구김이 덜하고 오래 입어도 형태가 유지되는 원단을 주로 추천합니다.", "원단 견본은 상담 때 직접 만져 보고 고르실 수 있습니다."]),
           ("관리 방법", ["입은 뒤에는 넓은 어깨 옷걸이에 걸어 하루 정도 바람을 쐬어 주세요. 잦은 드라이클리닝은 원단을 상하게 하므로 얼룩이 생겼을 때만 맡기시는 것이 좋습니다.", "바지는 밑단을 집게로 잡아 거꾸로 걸어 두면 주름이 자연스럽게 펴집니다.", "장기간 보관하실 때는 통기성 있는 커버를 씌워 직사광선을 피해 주세요."]),
           ("교환·환불 안내", [f"맞춤 제작 상품은 재단을 시작한 뒤에는 교환·환불이 어렵습니다. 자세한 기준 {NEED}", "가봉과 완성 단계에서 불편한 부분은 수선으로 맞춰 드립니다."]),
           ("매장 안내", [f"{n}: {a} · {t}" for n, _, a, t in STORES])]
    g = "".join(f'<div class="grp"><h3>{h}</h3>{"".join(f"<p>{x}</p>" for x in ps)}</div>' for h, ps in faq)
    page("guide.html", f"Guide | {BR}", f'<div class="layout-center"><div class="titleArea"><h2>Guide</h2></div><div class="faq">{g}</div></div>')

    page("company.html", BR, "")  # reference page has an empty body

    def listing(fn, title, desc, tabs, active, ids):
        t = "".join(f'<a href="{h}" class="{"on" if l == active else ""}">{l}</a>' for l, h in tabs)
        grid = f'<ul class="prdList">{"".join(f"<li class=item data-m-card>{card(i)}</li>" for i in ids)}</ul>' if ids else ''
        if ids:
            body = f"""<div class="prd-head"><h2>{title}</h2><div class="prd-desc"><p>{desc}</p></div></div>
<div class="middle-cate"><nav class="menuCategory">{t}</nav></div><div class="prd-list-wrap">{grid}</div>"""
        else:  # reference empty category: description line only, no title/tabs/message
            body = f"""<div class="prd-head"><div class="prd-desc" style="margin-top:52px"><p>{title}</p></div></div><div class="middle-cate"></div><div class="prd-list-wrap"></div>"""
        page(fn, f"{title} | {BR}", body)
    tabs = [("WEDDING LINE", "shop-men.html"), ("BUSINESS LINE", "shop-women.html"), ("BESPOKE", "shop-bespoke.html")]
    listing("shop-men.html", "MEN", "바론테일러의 남성 수트는 모두 매장에서 치수를 잰 뒤 제작합니다.<br>예식 날의 턱시도부터 출근길 수트까지<br>한 사람의 체형에 맞춰 한 벌씩 만듭니다.", tabs, "WEDDING LINE", range(1, 20))
    listing("shop-women.html", "WOMEN", "여성 테일러드 재킷과 셋업, 혼주 정장을 맞춤으로 제작합니다.<br>어깨와 허리선을 몸에 맞게 다시 그려<br>입는 순간 자세가 달라지는 옷을 만듭니다.", tabs, "BUSINESS LINE", [11, 6, 13, 16, 17, 20])
    listing("shop-bespoke.html", f"{BR} BESPOKE", "재단부터 마무리까지 손으로 완성하는 비스포크 라인입니다.<br>상담 예약 후 매장에서 원단과 디자인을 함께 고릅니다.", tabs, "BESPOKE", [])

    arc = [("AT HOME", "Aug, 2026", "가장 특별한 날에도, 평소의 나처럼 편하게 입는 예복."), ("WHITE TIE", "Jun, 2026", "흰 셔츠와 보타이, 단정함이 가장 잘 보이는 조합."),
           ("IVORY DAY", "Apr, 2026", "봄 예식을 위한 아이보리 더블 수트."), ("HER SUIT", "Mar, 2026", "어깨선을 살린 여성 테일러드 재킷."), ("QUIET BLACK", "Jan, 2026", "장식 없이 실루엣으로 말하는 블랙 수트.")]
    ac = "".join(f'<li class="item"><a class="thumb-box" href="archive.html">{img(f"arc-{i+1:02d}", t)}</a><div class="text-info"><div class="name">{t}</div><div class="when">{d}</div><p class="desc">{x}</p></div></li>' for i, (t, d, x) in enumerate(arc))
    page("archive.html", f"Archive | {BR}", f'<div class="archive"><div class="prd-list-wrap"><ul class="prdList">{ac}</ul></div></div>')
    page("lookbook.html", f"Lookbook | {BR}", '<div class="archive"><div class="prd-list-wrap"><ul class="prdList"></ul></div></div>')

    gal = ["prd-11-front", "prd-11-back", "detail-01", "detail-02", "detail-03", "detail-04", "prd-01-front", "prd-01-back", "prd-03-front", "prd-03-back"]
    sl = "".join(f'<div class="swiper-slide">{img(s, "")}</div>' for s in gal)
    detail = f"""<section class="detail-top"><div class="detail-right" data-m-slider-wrap><div class="sticky" data-m-sticky><div class="swiper" data-m-slider="detail"><div class="swiper-wrapper">{sl}</div></div><div class="swiper-pagination" data-m-dots></div>
<button class="nav prev" data-m-prev aria-label="이전">{ARROW_L}</button><button class="nav next" data-m-next aria-label="다음">{ARROW_R}</button></div></div>
<div class="detail-left"><div class="name">Ivory Tweed Jacket</div><div class="detail-info"><p>가격 {NEED}<br>Wool | Ivory | Jacket</p><p>모든 제품은 매장 상담 후 고객님의 체형을 직접 재어<br>제작합니다. 가봉 일정은 상담 때 함께 정합니다.</p></div>
<div class="detailArea"><div class="sheet"><figure>{img('prd-11-front', '')}<figcaption>JACKET</figcaption></figure><figure>{img('detail-01', '')}<figcaption>FABRIC</figcaption></figure><figure>{img('detail-02', '')}<figcaption>BUTTON</figcaption></figure><figure>{img('detail-03', '')}<figcaption>LAPEL</figcaption></figure></div></div></div></section>
<div class="sticky-watch" data-m-sticky-watch style="height:1px"></div>
<div class="detail-bottom-bnr"><div class="divide"><figure>{img('detail-banner', '')}</figure></div><div class="divide"><div class="dbb-text-inner">{logo()}<p>광주·순천 바론테일러 매장에 방문 예약을 남기시면<br>체형을 재고 원단을 함께 고를 수 있습니다.</p>
<div class="btn-wrap"><a class="btn" data-m-btn href="{KAKAO}" target="_blank" rel="noopener">방문 예약하기</a><a class="btn" data-m-btn href="stores.html">매장 찾기</a></div></div></div></div>"""
    page("detail.html", f"Ivory Tweed Jacket | {BR}", detail, "", True)

    def board(fn, title, rows, paginate=False, search=False, read="notice-read.html"):
        if rows:
            r = "".join(f'<div class="tr"><div class="number">{n}</div><div class="subject"><div class="prd_text"><a href="{read}">{s}</a></div><div class="board-right"><div class="writer">{BR}</div><div class="date">{d}</div></div></div></div>' for n, s, d in rows)
            lst = f'<div class="boardList">{r}</div>'
        else:
            lst = '<p class="board-empty">등록된 글이 없습니다.</p>'
        more = "<a>2</a><a>3</a><a>4</a><a>5</a>" if len(rows) > 5 else ""
        pg = f'<div class="ec-paginate"><a>&lsaquo;</a><a class="on">1</a>{more}<a>&rsaquo;</a></div>' if paginate else ""
        sr = '<form class="boardSearch" onsubmit="return false"><select data-m-field aria-label="기간"><option>일주일</option><option>한달</option><option>세달</option><option>전체</option></select><select data-m-field aria-label="항목"><option>제목</option><option>내용</option></select><input type="text" data-m-field aria-label="검색어"><a class="s-btn">검색</a></form>' if search else ""
        page(fn, f"{title} | {BR}", f'<div class="layout-center board-pkg{"" if rows else " empty"}"><div class="titleArea"><h2 class="light">{title}</h2></div>{lst}{pg}{sr}</div>')
    board("notice.html", "공지사항", [(3, "예식 시즌 상담 예약 안내", "2026-11-02"), (2, "체중 조절은 언제 하는 것이 좋을까요?", "2026-10-14"), (1, "바론테일러 홈페이지를 열었습니다", "2026-10-01")], paginate=True, search=True)
    rv = ["[Wedding] 웨딩거리 매장에서 맞춘 신랑 예복 후기", "[Wedding] 혼주 정장까지 한 번에 준비했어요", "[Business] 첫 출근 수트, 어깨가 편해요", "[Wedding] 아이보리 턱시도 가봉 두 번 받은 후기",
          "[Wedding] 순천점에서 형제가 같이 맞췄습니다", "[Business] 면접용 네이비 수트 후기", "[Wedding] 본식·2부 예복 두 벌 맞춤", "[Wedding] 체형이 달라도 잘 맞는 예복", "[Business] 겨울 플란넬 수트 후기", "[Wedding] 스냅 촬영용 예복 후기"]
    board("review.html", "Review", [(115 - i, s, f"26.{11 - i // 4:02d}.{28 - i * 2:02d}") for i, s in enumerate(rv)], paginate=True, search=True, read="review-read.html")
    board("product-review.html", "상품 사용후기", [], search=True)
    board("qna.html", "상품 Q&amp;A", [], search=True)

    def read(fn, title, subj, date, content, rating=False):
        rt = '<p><strong class="label">평점</strong>★★★★★</p>' if rating else ""
        body = f"""<div class="layout-center"><div class="titleArea"><h2>{title}</h2></div><div class="boardRead"><div class="title"><strong class="label">제목</strong>{subj}</div>
<div class="info">{rt}<p><strong class="label">작성자</strong>{BR}</p><p><strong class="label">작성일</strong>{date}</p><p><strong class="label">조회</strong>12</p></div>
<div class="content">{content}</div></div><div class="btnArea"><a class="btn" data-m-btn href="{'review.html' if rating else 'notice.html'}">목록</a></div></div>"""
        page(fn, f"{title} | {BR}", body)
    read("notice-read.html", "공지사항", "체중 조절은 언제 하는 것이 좋을까요?", "2026-10-14 11:20:00",
         "<p style='text-align:center'>안녕하세요, 바론테일러입니다.</p><p style='text-align:center'>상담 때 가장 많이 받는 질문 가운데 하나를 알려 드립니다.</p><br><p style='text-align:center'>예식을 앞두고 체중을 조절하실 계획이라면</p><p style='text-align:center'>마지막 가봉 전까지 목표 체중에 맞춰 두시는 것이 좋습니다.</p><p style='text-align:center'>가봉 이후 체중이 크게 바뀌면 허리와 어깨선을 다시 잡아야 할 수 있습니다.</p><p style='text-align:center'>일정이 애매하다면 상담 때 편하게 말씀해 주세요. 가봉 날짜를 함께 조정해 드립니다.</p><br><p style='text-align:center'>운동으로 몸을 키우실 계획이라면 어깨와 가슴 품에 여유를 조금 더 두고 재단합니다.</p><p style='text-align:center'>반대로 체중을 줄이실 계획이라면 첫 가봉을 조금 늦게 잡는 편이 좋습니다.</p><p style='text-align:center'>어느 쪽이든 마지막 가봉에서 한 번 더 맞추기 때문에 너무 걱정하지 않으셔도 됩니다.</p><br><p style='text-align:center'>궁금한 점은 오픈채팅이나 매장 전화로 언제든 물어봐 주세요.</p>")
    read("review-read.html", "Review", "[Wedding] 웨딩거리 매장에서 맞춘 신랑 예복 후기", "26.11.28",
         f"<p>상견례 끝나고 바로 예약해서 광주점에 다녀왔어요. 치수를 생각보다 훨씬 많이 재셔서 놀랐습니다.</p>{img('review-01', '')}<p>가봉 때 한쪽 어깨가 조금 낮다고 하셔서 그 부분까지 맞춰 주셨어요.</p>{img('review-02', '')}<p>본식 날 사진을 받아 보니 재킷이 들뜨지 않고 깔끔하게 떨어져서 만족합니다.</p>{img('review-03', '')}", rating=True)
    page("event-read.html", f"Event | {BR}", f"""<div class="layout-center"><div class="boardView" style="margin-top:50px"><div class="titleArea"><h2 class="big">겨울 예복 상담 이벤트</h2></div>
<p class="date-hit">Hit : 128</p><div class="share">{''.join('<a></a>' for _ in range(7))}</div><div style="padding:60px 0;font-size:var(--fs)">겨울 예식을 준비하시는 분들을 위한 상담 이벤트 안내입니다. 자세한 내용 {NEED}</div>
<a class="btn" data-m-btn href="event.html">LIST</a><p style="margin:50px 0 20px;font-size:var(--fs)">관리자에게만 댓글 작성 권한이 있습니다.</p><div style="border-top:1px solid #000;margin-top:30px;padding-top:40px;text-align:right;font-size:var(--fs)"><small style="font-size:10px">NEXT POST</small><br>가을 비즈니스 수트 이벤트</div></div></div>""")

    posters = [("photo", None), ("#b88a2e", "NOV"), ("#7a2f2c", "DEC"), ("#7a5a43", "SEPT"), ("#5aa59a", "AUG"), ("#5aa59a", "AUG"), ("#2f3a4a", "JUL"), ("#8a8f7a", "JUN"), ("#b88a2e", "MAY"), ("#7a2f2c", "APR"), ("#5aa59a", "MAR"), ("#7a5a43", "FEB"), ("#2f3a4a", "JAN")]
    tags = ["예복 상담 이벤트", "겨울 예복 패키지", "혼주 정장 패키지", "비즈니스 수트 패키지", "스냅 촬영 패키지", "얼리버드 코트", "여름 린넨 수트", "커플 예복 패키지", "봄 예복 패키지", "혼주 정장 패키지", "졸업 수트 패키지", "설 맞이 수트", "새해 첫 수트"]
    titles = ["겨울 예복 상담 이벤트", "11월 한정 예복 이벤트", "12월 혼주 정장 이벤트", "9월 비즈니스 수트 이벤트 (종료)", "8월 스냅 촬영 이벤트 (종료)", "8월 얼리버드 코트 이벤트 (종료)", "7월 린넨 수트 이벤트 (종료)", "6월 커플 예복 이벤트 (종료)", "5월 봄 예복 이벤트 (종료)", "4월 혼주 정장 이벤트 (종료)", "3월 졸업 수트 이벤트 (종료)", "2월 설 맞이 이벤트 (종료)", "1월 새해 수트 이벤트 (종료)"]
    ev = ""
    for i, (c, m) in enumerate(posters):
        inner = f'<div class="poster photo">{img("prd-02-front", "")}</div>' if c == "photo" else f'<div class="poster" style="background:{c}"><span class="seal"></span><span class="m">{m}</span><span class="p">PROMOTION</span><span class="e">EVENT</span><span class="tag">{tags[i]}</span></div>'
        ev += f'<a class="collection-article" href="event-read.html">{inner}<div class="text-info"><h2 style="font-size:13px;font-weight:500">{titles[i]}</h2></div></a>'
    page("event.html", f"Event | {BR}", f'<div class="article-wrap">{ev}</div>', "no-top")

    page("cart.html", f"Cart | {BR}", f"""<div class="layout-center"><div class="titleArea"><h2>Cart <span style="font-weight:300">(0)</span></h2></div>
<div class="basket"><div class="basket-left"><p class="board-empty" style="padding:30px 0">장바구니가 비어 있습니다.</p></div><div class="basket-right"><a class="btn" data-m-btn>장바구니 비우기</a><a class="btn s-btn" data-m-btn>주문하기</a>
<h4>장바구니 이용안내</h4><ul><li>바론테일러의 모든 수트는 매장 상담과 채촌 후 제작됩니다. 담아 두신 상품은 상담 때 함께 확인해 드립니다.</li></ul></div></div></div>""")
    print("built", len(glob.glob(f"{SITE}/*.html")), "pages")

if __name__ == "__main__":
    build()
