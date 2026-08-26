#!/usr/bin/env python3
"""Fan 的粉色天气同步天空生成器（西安）。

用 open-meteo（免费、无需 key）取西安当前天气，再生成两个粉色 SVG：
  - sky.svg       白天版（浅色主题显示）
  - sky-night.svg 夜间版（深色主题显示）
在 GitHub Actions 里每 3 小时跑一次并提交，即可让天空跟着真实天气变。
"""

import json
import os
import urllib.request

LAT, LON, TZ = 34.34, 108.94, "Asia/Shanghai"  # 西安

PINK = "#F4795B"
PINK_LIGHT = "#FBC7B3"
PINK_DEEP = "#E2542F"
PINK_FAINT = "#FFD9A0"

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


def header():
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 70" '
        'width="900" height="70" '
        'font-family="Segoe UI, Ubuntu, Helvetica, Arial, sans-serif">\n'
        "<title>sky</title>\n"
    )


def bg(opacity):
    return (
        '<rect width="900" height="70" '
        f'fill="{PINK}" opacity="{opacity}"/>\n'
    )


def sun(x=770, y=34):
    return (
        f'<g transform="translate({x},{y})">'
        f'<circle r="20" fill="{PINK}" opacity="0.16">'
        '<animate attributeName="opacity" values="0.10;0.28;0.10" '
        'dur="6s" repeatCount="indefinite"/></circle>'
        f'<circle r="12" fill="{PINK}"/>'
        f'<circle r="5.5" fill="{PINK_LIGHT}" opacity="0.8"/>'
        "</g>\n"
    )


def moon(x=770, y=30):
    return (
        f'<g transform="translate({x},{y})">'
        f'<circle r="12" fill="{PINK_LIGHT}"/>'
        f'<circle r="11" cx="-5" cy="-3" fill="{PINK_DEEP}"/>'
        "</g>\n"
    )


def stars(night):
    if not night:
        return ""
    s = ""
    for i, (cx, cy, r, d) in enumerate(
        [(80, 18, 1.3, 3.1), (150, 42, 1.0, 4.4), (240, 14, 1.2, 2.6),
         (360, 48, 1.1, 3.8), (540, 12, 1.3, 4.1), (680, 44, 1.0, 2.9)]
    ):
        s += (
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{PINK_LIGHT}">'
            f'<animate attributeName="opacity" values="0.1;0.9;0.1" dur="{d}s" '
            f'begin="{i * 0.5}s" repeatCount="indefinite"/></circle>'
        )
    return s + "\n"


def cloud(x, y, s=1.0):
    return (
        f'<g transform="translate({x},{y}) scale({s})" fill="{PINK}">'
        f'<g opacity="0.75">'
        f'<ellipse cx="-34" cy="0" rx="26" ry="13"/>'
        f'<ellipse cx="0" cy="-9" rx="30" ry="16"/>'
        f'<ellipse cx="34" cy="0" rx="26" ry="13"/>'
        f'<rect x="-34" y="0" width="68" height="13" rx="6.5"/>'
        "</g>"
        '<animateTransform attributeName="transform" type="translate" '
        'values="0 0; 12 0; 0 0" dur="11s" repeatCount="indefinite"/>'
        "</g>\n"
    )


def rain():
    lines = ""
    for i, (x, d) in enumerate(
        [(70, 0.0), (170, 0.6), (270, 0.2), (370, 0.8), (470, 0.4),
         (570, 0.9), (670, 0.1), (770, 0.5)]
    ):
        lines += (
            f'<line x1="{x}" y1="10" x2="{x}" y2="26" stroke="{PINK}" '
            'stroke-width="2" stroke-linecap="round" opacity="0.65">'
            f'<animate attributeName="opacity" values="0.1;0.8;0.1" dur="1.2s" '
            f'begin="{d}s" repeatCount="indefinite"/></line>'
        )
    return lines + "\n"


def snow():
    out = ""
    for i, (x, cy, d) in enumerate(
        [(90, 20, 0.0), (200, 32, 0.5), (310, 18, 0.2), (420, 30, 0.8),
         (530, 20, 0.4), (640, 34, 0.9), (750, 18, 0.1)]
    ):
        out += (
            f'<circle cx="{x}" cy="{cy}" r="2.6" fill="{PINK_LIGHT}">'
            f'<animate attributeName="cy" values="{cy - 6};{cy + 8};{cy - 6}" '
            f'dur="3.2s" begin="{d}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0.2;0.9;0.2" dur="3.2s" '
            f'begin="{d}s" repeatCount="indefinite"/></circle>'
        )
    return out + "\n"


def fog():
    return (
        f'<g fill="{PINK}" opacity="0.35">'
        '<ellipse cx="230" cy="26" rx="150" ry="9"/>'
        '<ellipse cx="560" cy="44" rx="180" ry="10"/>'
        '<animateTransform attributeName="transform" type="translate" '
        'values="0 0; 20 0; 0 0" dur="14s" repeatCount="indefinite"/>'
        "</g>\n"
    )


def storm():
    return (
        cloud(300, 30, 1.2)
        + cloud(600, 28, 1.0)
        + (
            f'<g transform="translate(452,40)">'
            f'<path d="M0 0 L-7 16 L0 16 L-5 30 L8 11 L1 11 L7 0 Z" '
            f'fill="{PINK}">'
            '<animate attributeName="opacity" values="0;1;0;1;0" '
            'keyTimes="0;0.15;0.4;0.6;1" dur="3.5s" repeatCount="indefinite"/>'
            "</path></g>\n"
        )
    )


def build_sky(scene_name, night):
    out = header()
    out += bg(0.06 if not night else 0.10)
    if night:
        out += moon()
        out += stars(True)
    else:
        out += sun()

    if scene_name == "clear":
        pass
    elif scene_name == "clouds":
        out += cloud(300, 34, 1.1) + cloud(620, 40, 0.9)
    elif scene_name == "rain":
        out += cloud(300, 24, 1.1) + cloud(620, 20, 0.9) + rain()
    elif scene_name == "snow":
        out += cloud(300, 22, 1.1) + snow()
    elif scene_name == "fog":
        out += fog()
    elif scene_name == "storm":
        out += storm()
    out += "</svg>\n"
    return out


def main():
    weather = fetch_weather()
    sc = scene(weather["code"])
    day = build_sky(sc, night=False)
    night = build_sky(sc, night=True)
    with open(os.path.join(OUT_DIR, "sky.svg"), "w", encoding="utf-8") as f:
        f.write(day)
    with open(os.path.join(OUT_DIR, "sky-night.svg"), "w", encoding="utf-8") as f:
        f.write(night)
    print(f"scene={sc} code={weather['code']} temp={weather['temp']} is_day={weather['is_day']}")


if __name__ == "__main__":
    main()
