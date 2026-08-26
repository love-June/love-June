#!/usr/bin/env python3
"""Fan 的橘色天气同步天空生成器（西安）。

用 open-meteo（免费、无需 key）取西安当前天气，生成精致的橘色天空 SVG：
  - sky.svg       白天版（浅色主题显示）
  - sky-night.svg 夜间版（深色主题显示）
在 GitHub Actions 里每 3 小时跑一次并提交，天空就会跟着西安真实天气变。
"""

import json
import os
import urllib.request

LAT, LON, TZ = 34.34, 108.94, "Asia/Shanghai"  # 西安

# 橘色调色板（与横幅/页脚一致）
MAIN = "#F4795B"
DEEP = "#E2542F"
PEACH = "#ED8B66"
LIGHT = "#FBC7B3"
SUN_CORE = "#FFD9A0"
SUN_GLOW = "#FFC069"
NIGHT_BG = "#2C3E63"
NIGHT_STAR = "#FFE9CF"

FONT = "Segoe UI, Ubuntu, Helvetica, Arial, sans-serif"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def fetch_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        "&current_weather=true"
        f"&timezone={TZ}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "fan-profile-scene"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    cw = data.get("current_weather", {})
    return {
        "code": int(cw.get("weathercode", 0)),
        "is_day": int(cw.get("is_day", 1)),
        "temp": cw.get("temperature"),
    }


def scene(code):
    if code == 0:
        return "clear"
    if code in (1, 2, 3):
        return "clouds"
    if code in (45, 48):
        return "fog"
    if code in (95, 96, 99):
        return "storm"
    if code in (71, 73, 75, 77, 85, 86):
        return "snow"
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        return "rain"
    return "clear"


def svg_open():
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 70" '
        'width="900" height="70" font-family="%s">\n<title>sky</title>\n' % FONT
    )


def defs(night):
    d = "<defs>\n"
    if night:
        d += (
            '<linearGradient id="skybg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{NIGHT_BG}" stop-opacity="0.28"/>'
            f'<stop offset="1" stop-color="{MAIN}" stop-opacity="0.05"/>'
            "</linearGradient>"
        )
    else:
        d += (
            '<linearGradient id="skybg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{LIGHT}" stop-opacity="0.25"/>'
            f'<stop offset="1" stop-color="{MAIN}" stop-opacity="0.05"/>'
            "</linearGradient>"
        )
    d += (
        '<radialGradient id="glow">'
        f'<stop offset="0" stop-color="{SUN_CORE}" stop-opacity="0.9"/>'
        f'<stop offset="1" stop-color="{SUN_GLOW}" stop-opacity="0"/>'
        "</radialGradient>"
        '<linearGradient id="cloudg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#FFFFFF" stop-opacity="0.8"/>'
        f'<stop offset="1" stop-color="{LIGHT}" stop-opacity="0.2"/>'
        "</linearGradient>"
        '<linearGradient id="clouddark" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{DEEP}" stop-opacity="0.9"/>'
        f'<stop offset="1" stop-color="{PEACH}" stop-opacity="0.35"/>'
        "</linearGradient>"
    )
    d += "</defs>\n"
    return d


def bg():
    return '<rect width="900" height="70" fill="url(#skybg)"/>\n'


def sun(x=782, y=34):
    rays = "".join(
        f'<path d="M0 -22 L1.7 -31 L-1.7 -31 Z" fill="{SUN_GLOW}" '
        f'transform="rotate({a})"/>'
        for a in range(0, 360, 45)
    )
    return (
        f'<g transform="translate({x},{y})">'
        '<circle r="34" fill="url(#glow)">'
        '<animate attributeName="opacity" values="0.7;1;0.7" dur="6s" '
        'repeatCount="indefinite"/></circle>'
        f'<g opacity="0.5"><animateTransform attributeName="transform" '
        'type="rotate" from="0" to="360" dur="90s" repeatCount="indefinite"/>'
        f'{rays}</g>'
        f'<circle r="13" fill="{SUN_CORE}"/>'
        '<circle r="6" fill="#FFFFFF" opacity="0.7"/>'
        "</g>\n"
    )


def moon(x=782, y=30):
    return (
        f'<g transform="translate({x},{y})">'
        '<circle r="30" fill="url(#glow)">'
        '<animate attributeName="opacity" values="0.6;1;0.6" dur="7s" '
        'repeatCount="indefinite"/></circle>'
        f'<circle r="12" fill="{LIGHT}"/>'
        f'<circle r="12" cy="-3" fill="{NIGHT_BG}" opacity="0.18"/>'
        f'<circle cx="4" cy="5" r="2.2" fill="{PEACH}" opacity="0.55"/>'
        f'<circle cx="-4" cy="-5" r="1.5" fill="{PEACH}" opacity="0.5"/>'
        f'<circle cx="5" cy="-4" r="1.1" fill="{PEACH}" opacity="0.45"/>'
        "</g>\n"
    )


def stars(night):
    if not night:
        return ""
    out = ""
    pts = [
        (70, 16, 1.6, 3.2, 0.0), (130, 40, 1.1, 4.6, 0.5), (210, 12, 1.5, 2.8, 1.0),
        (320, 46, 1.2, 3.9, 1.5), (430, 14, 1.7, 4.2, 2.0), (560, 42, 1.1, 3.0, 2.5),
        (650, 15, 1.4, 4.8, 3.0), (740, 48, 1.0, 3.5, 3.5), (860, 12, 1.3, 3.1, 4.0),
    ]
    for cx, cy, r, dur, begin in pts:
        out += (
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{NIGHT_STAR}">'
            f'<animate attributeName="opacity" values="0.15;0.95;0.15" dur="{dur}s" '
            f'begin="{begin}s" repeatCount="indefinite"/></circle>'
        )
    for cx, cy, dur in [(180, 30, 4.0), (500, 18, 5.2), (700, 30, 4.6)]:
        out += (
            f'<g transform="translate({cx},{cy})" fill="{NIGHT_STAR}">'
            f'<path d="M0 -5 L1 -1 L5 0 L1 1 L0 5 L-1 1 L-5 0 L-1 -1 Z">'
            f'<animate attributeName="opacity" values="0;0.9;0" dur="{dur}s" '
            f'repeatCount="indefinite"/></path></g>'
        )
    out += (
        '<g opacity="0">'
        '<animate attributeName="opacity" values="0;0.9;0.9;0" keyTimes="0;0.08;0.5;0.6" '
        'dur="12s" begin="3s" repeatCount="indefinite"/>'
        '<line x1="0" y1="0" x2="-28" y2="14" stroke="#FFFFFF" stroke-width="1.4" '
        'stroke-linecap="round">'
        '<animateMotion dur="12s" begin="3s" repeatCount="indefinite" '
        'path="M820 4 L680 40"/></line></g>'
    )
    return out + "\n"


def cloud(x, y, s=1.0, dark=False):
    fill = "url(#clouddark)" if dark else "url(#cloudg)"
    return (
        f'<g transform="translate({x},{y}) scale({s})">'
        '<g>'
        '<animateTransform attributeName="transform" type="translate" '
        'values="0 0; 13 0; 0 0" dur="13s" repeatCount="indefinite"/>'
        f'<ellipse cx="-38" cy="2" rx="28" ry="14" fill="{fill}"/>'
        f'<ellipse cx="0" cy="-9" rx="34" ry="18" fill="{fill}"/>'
        f'<ellipse cx="38" cy="2" rx="28" ry="14" fill="{fill}"/>'
        f'<rect x="-38" y="2" width="76" height="14" rx="7" fill="{fill}"/>'
        "</g></g>\n"
    )


def rain():
    drops = ""
    for x, delay in [
        (60, 0.0), (150, 0.3), (240, 0.6), (330, 0.1), (420, 0.7),
        (510, 0.4), (600, 0.9), (690, 0.2), (780, 0.5), (870, 0.8),
    ]:
        drops += (
            f'<line x1="{x}" y1="14" x2="{x - 6}" y2="34" stroke="{MAIN}" '
            'stroke-width="2" stroke-linecap="round">'
            f'<animate attributeName="opacity" values="0.1;0.85;0.1" dur="1.1s" '
            f'begin="{delay}s" repeatCount="indefinite"/></line>'
        )
    splashes = "".join(
        f'<circle cx="{x}" cy="46" r="1.4" fill="{LIGHT}">'
        f'<animate attributeName="opacity" values="0;0.7;0" dur="1.4s" '
        f'begin="{delay}s" repeatCount="indefinite"/></circle>'
        for x, delay in [(100, 0.2), (280, 0.5), (460, 0.8), (640, 0.1), (820, 0.6)]
    )
    return drops + splashes + "\n"


def snow():
    out = ""
    for x, cy, r, dur, begin in [
        (80, 22, 2.8, 3.0, 0.0), (180, 34, 2.1, 3.6, 0.5), (290, 18, 2.6, 2.8, 0.2),
        (400, 30, 2.0, 3.9, 0.8), (510, 20, 2.7, 3.2, 0.4), (620, 36, 2.2, 3.5, 0.9),
        (730, 19, 2.5, 2.9, 0.1), (840, 32, 2.0, 3.8, 0.6),
    ]:
        out += (
            f'<circle cx="{x}" cy="{cy}" r="{r}" fill="{LIGHT}">'
            f'<animate attributeName="cy" values="{cy - 4};{cy + 14};{cy - 4}" '
            f'dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0.2;0.95;0.2" dur="{dur}s" '
            f'begin="{begin}s" repeatCount="indefinite"/></circle>'
        )
    return out + "\n"


def fog():
    return (
        '<g fill="#FFFFFF" opacity="0.22">'
        '<ellipse cx="180" cy="20" rx="150" ry="9"/>'
        '<ellipse cx="520" cy="38" rx="200" ry="11"/>'
        '<ellipse cx="760" cy="24" rx="130" ry="8"/>'
        '<animateTransform attributeName="transform" type="translate" '
        'values="0 0; 22 0; 0 0" dur="15s" repeatCount="indefinite"/>'
        "</g>\n"
    )


def lightning(x, y):
    return (
        f'<g transform="translate({x},{y})">'
        f'<path d="M0 0 L-8 18 L0 18 L-6 34 L10 10 L2 10 L9 0 Z" '
        f'fill="{SUN_CORE}">'
        '<animate attributeName="opacity" values="0;1;0;1;0" '
        'keyTimes="0;0.12;0.3;0.45;1" dur="3.2s" repeatCount="indefinite"/>'
        "</path></g>\n"
    )


def storm():
    return cloud(280, 26, 1.25, dark=True) + cloud(640, 24, 1.05, dark=True) \
        + lightning(460, 34) + lightning(700, 32) + rain()


def birds():
    head = (
        '<g stroke="%s" stroke-width="1.6" fill="none" stroke-linecap="round" '
        'opacity="0.55">' % DEEP
    )
    return (
        head
        + '<g><path d="M0 0 Q5 -5 10 0 Q15 -5 20 0"/>'
        + '<animateMotion dur="20s" begin="1s" repeatCount="indefinite" '
        + 'path="M120 22 L860 12"/></g>'
        + '<g><path d="M0 0 Q4 -4 8 0 Q12 -4 16 0"/>'
        + '<animateMotion dur="24s" begin="5s" repeatCount="indefinite" '
        + 'path="M80 34 L820 24"/></g>'
        + "</g>\n"
    )


def build_sky(scene_name, night):
    out = svg_open() + defs(night) + bg()
    if night:
        out += moon() + stars(True)
    else:
        out += sun()

    if scene_name == "clear":
        if not night:
            out += cloud(360, 20, 0.8) + cloud(600, 12, 0.6) + birds()
    elif scene_name == "clouds":
        out += cloud(300, 34, 1.15) + cloud(620, 40, 0.95) + cloud(130, 18, 0.7)
    elif scene_name == "rain":
        out += cloud(300, 22, 1.2, dark=True) + cloud(640, 18, 1.0, dark=True) + rain()
    elif scene_name == "snow":
        out += cloud(300, 22, 1.15) + snow()
    elif scene_name == "fog":
        out += fog()
    elif scene_name == "storm":
        out += storm()

    out += "</svg>\n"
    return out


def main():
    weather = fetch_weather()
    sc = scene(weather["code"])
    with open(os.path.join(OUT_DIR, "sky.svg"), "w", encoding="utf-8") as f:
        f.write(build_sky(sc, night=False))
    with open(os.path.join(OUT_DIR, "sky-night.svg"), "w", encoding="utf-8") as f:
        f.write(build_sky(sc, night=True))
    print(f"scene={sc} code={weather['code']} temp={weather['temp']} is_day={weather['is_day']}")


if __name__ == "__main__":
    main()
