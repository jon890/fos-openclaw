#!/usr/bin/env python3
import json
import re
import sys
from html import unescape
from urllib.parse import parse_qs, urlparse

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

FALLBACK_URLS = [
    "https://m.land.naver.com/complex/info/1649",
    "https://fin.land.naver.com/complexes/1649?tab=detail",
    "https://fin.land.naver.com/complexes/1652?articleTradeTypes=A1&isVilla=false&tab=article&articleSortingType=PRICE_ASC",
]


def compact(text):
    return re.sub(r"\s+", " ", unescape(text or "")).strip()


def extract_title(html):
    m = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    return compact(m.group(1)) if m else ""


def classify_response(response):
    final_url = response.url
    if final_url.endswith("/404"):
        return "fallback-404"
    if "fin.land.naver.com/map" in final_url:
        return "legacy-map-redirect"
    if "fin.land.naver.com/complexes/" in final_url and response.status_code == 200:
        return "complex-entry-ok"
    if response.status_code == 200:
        return "ok"
    return f"http-{response.status_code}"


def fetch(url):
    return requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)


def extract_payload_hints(html):
    hints = {}
    if "self.__next_f.push" in html:
        hints["nextFlightPayload"] = True
    scripts = len(re.findall(r"<script", html, re.I))
    hints["scriptCount"] = scripts
    for kw in ["articleTradeTypes", "articleSortingType", "tradeTypes", "realEstateTypes", "map?layer="]:
        if kw in html:
            hints.setdefault("keywords", []).append(kw)
    return hints


def extract_map_state(final_url):
    parsed = urlparse(final_url)
    qs = parse_qs(parsed.query)
    state = {}
    for key in ["center", "zoom", "tradeTypes", "realEstateTypes", "space", "layer"]:
        if key in qs:
            state[key] = qs[key][0]
    return state


def main():
    url = sys.argv[1]
    tried = []

    candidates = [url] + [u for u in FALLBACK_URLS if u != url]
    selected = None
    selected_url = None

    for candidate_url in candidates:
        response = fetch(candidate_url)
        status = classify_response(response)
        tried.append({
            "url": candidate_url,
            "finalUrl": response.url,
            "status": response.status_code,
            "classifiedStatus": status,
        })
        if selected is None:
            selected = response
            selected_url = candidate_url
        if status in ("complex-entry-ok", "legacy-map-redirect", "ok"):
            selected = response
            selected_url = candidate_url
            break

    title = extract_title(selected.text)
    text = compact(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", " ", selected.text, flags=re.I | re.S)))
    status = classify_response(selected)
    payload_hints = extract_payload_hints(selected.text)
    map_state = extract_map_state(selected.url)

    note = "네이버 fin.land 진입점은 확보됐지만, 현재는 Next/JS shell과 map 상태까지만 확인된다. 정적 HTML에서 매물/가격 수치가 직접 드러나지 않는다."
    if status == "complex-entry-ok":
        note = "Naver Land complexes 진입은 성공했지만, 내부적으로 추가 데이터 로딩이 필요한 구조다."
    elif status == "legacy-map-redirect":
        note = "complexes 또는 m.land 경로는 fin.land map shell로 연결된다. 유효한 진입점은 확보됐고, 다음 단계는 payload/API 추적이다."
    elif status == "fallback-404":
        note = "현재 등록된 Naver Land URL은 404 fallback이다."

    result = {
        "name": "Naver Land",
        "url": url,
        "resolvedUrl": selected_url,
        "finalUrl": selected.url,
        "status": status,
        "host": urlparse(selected.url).netloc,
        "title": title,
        "description": "",
        "signals": [kw for kw in ["단지", "지도", "매물", "시세"] if kw in text],
        "numericSignals": {},
        "jsonLd": [],
        "triedUrls": tried,
        "payloadHints": payload_hints,
        "mapState": map_state,
        "note": note,
    }

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
