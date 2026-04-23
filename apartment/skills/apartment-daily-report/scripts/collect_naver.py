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
    for kw in ["articleTradeTypes", "articleSortingType", "tradeTypes", "realEstateTypes", "map?layer=", "complexes/"]:
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


def extract_json_blobs(html):
    blobs = []
    for match in re.finditer(r"self\.__next_f\.push\((.*?)\);", html, re.S):
        blob = compact(match.group(1))
        if blob and blob not in blobs:
            blobs.append(blob[:4000])
    return blobs[:5]


def extract_numeric_signals(text):
    numeric = {}

    m = re.search(r"(\d{1,4})세대", text)
    if m:
        numeric["households"] = int(m.group(1))

    m = re.search(r"(\d{2,4})동", text)
    if m:
        numeric["buildingCount"] = int(m.group(1))

    completion = re.search(r"(?:사용승인|준공|입주)\s*(\d{4})\.?\s*(\d{1,2})?", text)
    if completion:
        numeric["completionYear"] = int(completion.group(1))
        if completion.group(2):
            numeric["completionMonth"] = int(completion.group(2))

    area_range = re.search(r"([0-9.]+\s*㎡\s*[~\-]\s*[0-9.]+\s*㎡)", text)
    if area_range:
        numeric["areaRange"] = compact(area_range.group(1))

    article_counts = {}
    for label in ["매매", "전세", "월세"]:
        m = re.search(rf"{label}\s*(\d+)건", text)
        if m:
            article_counts[label] = int(m.group(1))
    if article_counts:
        numeric["articleCounts"] = article_counts

    return numeric


def build_snippets(text):
    snippets = []
    for kw in ["세대", "매매", "전세", "월세", "사용승인", "준공", "입주"]:
        idx = text.find(kw)
        if idx >= 0:
            snippet = compact(text[max(0, idx - 80): idx + 220])
            if snippet and snippet not in snippets:
                snippets.append(snippet)
    return snippets[:5]


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
    numeric_signals = extract_numeric_signals(text)
    json_blobs = extract_json_blobs(selected.text)
    snippets = build_snippets(text)

    note = "네이버 fin.land 진입점은 확보됐지만, 현재는 Next/JS shell과 map 상태까지만 확인된다. 정적 HTML에서 매물/가격 수치가 제한적으로만 보인다."
    if numeric_signals.get("articleCounts"):
        counts = numeric_signals["articleCounts"]
        note = f"Naver Land에서 정적 HTML 기준 매물 카운트 일부를 읽었다: 매매 {counts.get('매매', '?')} / 전세 {counts.get('전세', '?')} / 월세 {counts.get('월세', '?')}."
    elif status == "complex-entry-ok":
        note = "Naver Land complexes 진입은 성공했지만, 내부적으로 추가 데이터 로딩이 필요한 구조다."
    elif status == "legacy-map-redirect":
        note = "complexes 또는 m.land 경로는 fin.land map shell로 연결된다. 유효한 진입점은 확보됐고, 정적 HTML에서 읽히는 신호는 제한적이다."
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
        "signals": [kw for kw in ["단지", "지도", "매물", "시세", "전세", "월세"] if kw in text],
        "numericSignals": numeric_signals,
        "jsonLd": [],
        "triedUrls": tried,
        "payloadHints": payload_hints,
        "mapState": map_state,
        "nextFlightBlobs": json_blobs,
        "snippets": snippets,
        "note": note,
    }

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
