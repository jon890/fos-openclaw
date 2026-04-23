#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from datetime import datetime

TARGET_NAME = os.environ.get("TARGET_NAME", "엘지원앙아파트")
TARGET_ALIAS = os.environ.get("TARGET_ALIAS", "LG원앙")
TARGET_LOCATION = os.environ.get("TARGET_LOCATION", "경기 구리시 수택동 854-2 / 체육관로 54")
TARGET_UNIT_LABEL = os.environ.get("TARGET_UNIT_LABEL", "59A")
TARGET_UNIT_EXCLUSIVE_AREA_M2 = float(os.environ.get("TARGET_UNIT_EXCLUSIVE_AREA_M2", "59"))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NAVER_URL = os.environ.get("NAVER_LAND_URL", "https://new.land.naver.com/complexes/1649?tab=detail&rf=Y")
NAVER_BROWSER_ENABLED = os.environ.get("NAVER_BROWSER_ENABLED", "0") == "1"

SOURCES = [
    {
        "name": "Naver Land",
        "url": NAVER_URL,
        "script": os.path.join(SCRIPT_DIR, "collect_naver.py"),
    },
    {
        "name": "Hogangnono",
        "url": os.environ.get("HOGANGNONO_URL", "https://hogangnono.com/apt/5V184"),
        "script": os.path.join(SCRIPT_DIR, "collect_hogangnono.py"),
    },
    {
        "name": "KB Land",
        "url": os.environ.get("KB_LAND_URL", "https://kbland.kr/se/c/2906"),
        "script": os.path.join(SCRIPT_DIR, "collect_kbland.py"),
    },
]


def run_source(script, url):
    proc = subprocess.run([sys.executable, script, url], capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


def get_source(source_results, name):
    return next((src for src in source_results if src.get("name") == name), {})


def maybe_collect_naver_browser(source_results, notes):
    if not NAVER_BROWSER_ENABLED:
        return

    naver = get_source(source_results, "Naver Land")
    weak_static = naver.get("status") == "legacy-map-redirect" and not naver.get("numericSignals", {}).get("articleCounts")
    if not weak_static:
        return

    script = os.path.join(SCRIPT_DIR, "collect_naver_browser.py")
    try:
        browser_result = run_source(script, NAVER_URL)
        source_results.append(browser_result)
        notes.append(f"Naver browser fallback 상태: {browser_result.get('status', 'unknown')}")
    except Exception as e:
        notes.append(f"Naver browser fallback 실패: {type(e).__name__}")


def classify_focus_against_profiles(type_profiles):
    matches = []
    for profile in type_profiles:
        exclusive = profile.get("exclusiveAreaEstimateM2")
        if exclusive is None:
            continue
        if abs(exclusive - TARGET_UNIT_EXCLUSIVE_AREA_M2) <= 1.5:
            matches.append(profile)
    return matches


def build_recent_transactions(source_results):
    hogang = get_source(source_results, "Hogangnono")
    kb = get_source(source_results, "KB Land")
    type_profiles = kb.get("numericSignals", {}).get("typeProfiles", [])
    known_supply_areas = {int(round(p.get("supplyAreaM2", 0))): p for p in type_profiles if p.get("supplyAreaM2") is not None}

    rows = []
    for item in hogang.get("recentTransactions", []):
        row = dict(item)
        supply_area = row.get("supplyAreaApprox")
        if supply_area and supply_area in known_supply_areas:
            profile = known_supply_areas[supply_area]
            row.setdefault("unit", f"{supply_area}㎡")
            row["sourceTypeProfile"] = {
                "typeLabel": profile.get("typeLabel"),
                "exclusiveAreaEstimateM2": profile.get("exclusiveAreaEstimateM2"),
            }
        rows.append(row)
    return rows


def build_listing_summary(source_results):
    kb = get_source(source_results, "KB Land")
    pricing = kb.get("numericSignals", {}).get("pricing", {})
    listing_counts = kb.get("numericSignals", {}).get("listingCounts", {})
    notes = []

    if listing_counts:
        notes.append(f"KB Land 기준 매물 수: 매매 {listing_counts.get('매매', '?')}건, 전세 {listing_counts.get('전세', '?')}건, 월세 {listing_counts.get('월세', '?')}건")
    if kb.get("numericSignals", {}).get("areaRange"):
        notes.append(f"KB Land 기준 공급면적 범위: {kb['numericSignals']['areaRange']}")

    type_profiles = kb.get("numericSignals", {}).get("typeProfiles", [])
    focus_matches = classify_focus_against_profiles(type_profiles)
    if focus_matches:
        notes.append(f"KB Land 타입 프로필에서 전용 {int(TARGET_UNIT_EXCLUSIVE_AREA_M2)}㎡ 근사 매칭 {len(focus_matches)}개 확인")
    elif type_profiles:
        notes.append(f"KB Land 타입 프로필상 전용 {int(TARGET_UNIT_EXCLUSIVE_AREA_M2)}㎡ 근사 매칭이 보이지 않음")

    browser = get_source(source_results, "Naver Land Browser")
    browser_counts = browser.get("numericSignals", {}).get("listingCounts", {}) if browser else {}
    if browser_counts:
        notes.append(
            f"Naver browser 기준 매물 수: 매매 {browser_counts.get('sale', '?')} / 전세 {browser_counts.get('jeonse', '?')} / 월세 {browser_counts.get('wolse', '?')}"
        )

    return {
        "status": "partial" if pricing else "limited",
        "counts": listing_counts,
        "pricing": pricing,
        "typeProfiles": type_profiles,
        "focusUnit": TARGET_UNIT_LABEL,
        "focusAreaMatches": focus_matches,
        "notes": notes or ["구조화된 매물 요약을 충분히 추출하지 못했다."],
    }


def build_comparison(source_results):
    naver = get_source(source_results, "Naver Land")
    browser = get_source(source_results, "Naver Land Browser")
    hogang = get_source(source_results, "Hogangnono")
    kb = get_source(source_results, "KB Land")

    return {
        "naver": naver.get("note", "Naver Land 확인 결과 없음"),
        "naverBrowser": browser.get("note", "Naver browser fallback 결과 없음") if browser else "Naver browser fallback 결과 없음",
        "hogangnono": hogang.get("note", "호갱노노 확인 결과 없음"),
        "kbland": kb.get("note", "KB Land 확인 결과 없음"),
    }


def main():
    if len(sys.argv) != 2:
        print("usage: collect_sources.py <output-json>", file=sys.stderr)
        sys.exit(1)

    out_path = sys.argv[1]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    source_results = []
    notes = []

    for src in SOURCES:
        try:
            source_results.append(run_source(src["script"], src["url"]))
        except Exception as e:
            source_results.append({
                "name": src["name"],
                "url": src["url"],
                "status": "error",
                "note": f"수집 실패: {type(e).__name__}: {e}",
            })
            notes.append(f"{src['name']} 수집 실패: {type(e).__name__}")

    maybe_collect_naver_browser(source_results, notes)

    hogang = get_source(source_results, "Hogangnono")
    kb = get_source(source_results, "KB Land")
    naver = get_source(source_results, "Naver Land")
    naver_browser = get_source(source_results, "Naver Land Browser")

    if naver.get("numericSignals", {}).get("articleCounts"):
        counts = naver["numericSignals"]["articleCounts"]
        notes.append(f"Naver Land 정적 HTML 기준 매물 수 일부 추출: 매매 {counts.get('매매', '?')}건, 전세 {counts.get('전세', '?')}건, 월세 {counts.get('월세', '?')}건")
    elif naver.get("status") == "legacy-map-redirect":
        notes.append("Naver Land는 new.land 직접 URL 대신 m.land -> fin.land map redirect 경로와 제한적 정적 신호까지만 복구했다.")

    if naver_browser:
        notes.append(f"Naver browser fallback note: {naver_browser.get('note', '없음')}")

    if hogang.get("numericSignals", {}).get("areaTradeSummary"):
        area = hogang["numericSignals"]["areaTradeSummary"]
        notes.append(f"호갱노노에서 {area['areaLabel']} 최근 1개월 평균 {area['monthlyAverage']} 추출")
    if kb.get("numericSignals", {}).get("pricing", {}).get("매매", {}).get("general"):
        notes.append(f"KB Land에서 매매 일반가 {kb['numericSignals']['pricing']['매매']['general']} 추출")
    focus_matches = classify_focus_against_profiles(kb.get("numericSignals", {}).get("typeProfiles", []))
    if focus_matches:
        notes.append(f"KB Land 타입 정보 기준 전용 {int(TARGET_UNIT_EXCLUSIVE_AREA_M2)}㎡ 후보를 찾음")
    elif kb.get("numericSignals", {}).get("typeProfiles"):
        notes.append(f"KB Land 타입 정보 기준 전용 {int(TARGET_UNIT_EXCLUSIVE_AREA_M2)}㎡ 후보를 찾지 못함")

    out = {
        "generatedAt": datetime.now().isoformat(),
        "target": {
            "name": TARGET_NAME,
            "alias": TARGET_ALIAS,
            "location": TARGET_LOCATION,
            "focusUnit": {
                "label": TARGET_UNIT_LABEL,
                "exclusiveAreaM2": TARGET_UNIT_EXCLUSIVE_AREA_M2,
            },
        },
        "sources": source_results,
        "recentTransactions": build_recent_transactions(source_results),
        "listingSummary": build_listing_summary(source_results),
        "comparison": build_comparison(source_results),
        "notes": notes + [
            "collector -> normalize -> Claude synthesis 구조는 유지했다.",
            "runner의 Discord 알림 경로는 변경하지 않았다.",
            "수집 결과에 없는 값은 Claude가 채우지 말고 불확실성으로 남겨야 한다.",
        ],
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
