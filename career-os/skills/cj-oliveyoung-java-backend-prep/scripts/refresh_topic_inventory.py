#!/usr/bin/env python3
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

TASK_ROOT = Path.home() / 'ai-nodes' / 'career-os'
CONFIG = TASK_ROOT / 'config'
RUNTIME = TASK_ROOT / 'data' / 'runtime'
RUNTIME.mkdir(parents=True, exist_ok=True)
HISTORY_PATH = RUNTIME / 'topic-inventory-history.jsonl'

# ADR-010: 추천 점수 기반 + mix target
MIX_TARGET = {'new': 2, 'deepen': 1, 'review': 1, 'live-coding': 1}
WEAK_AREAS = {'mysql', 'redis'}
WEAK_AREA_BONUS = 3
RECENT_PENALTY_PER = 2
CARRYOVER_PENALTY = 1
TAG_PRIORITY = {'new': 0, 'deepen': -1, 'review': -2, 'live-coding': 0}


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_yesterday_keys():
    if not HISTORY_PATH.exists():
        return set()
    last = None
    try:
        with HISTORY_PATH.open(encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    last = line
    except OSError:
        return set()
    if not last:
        return set()
    try:
        return set(json.loads(last).get('keys', []))
    except json.JSONDecodeError:
        return set()


def append_history(keys):
    entry = {'generatedAt': datetime.now(timezone.utc).isoformat(), 'keys': list(keys)}
    with HISTORY_PATH.open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


study_topics = read_json(CONFIG / 'study-pack-topics.json')
study_candidates = read_json(CONFIG / 'study-topic-candidates.json').get('topics', [])
live_seeds = read_json(CONFIG / 'live-coding-seed-pool.json').get('seeds', [])
live_seed_candidates = read_json(CONFIG / 'live-coding-seed-candidates.json').get('seeds', [])
artifacts = read_json(TASK_ROOT / 'data' / 'generated-artifacts.json').get('artifacts', [])

study_paths = {a.get('outputPath') for a in artifacts if a.get('kind') == 'study-pack'}
live_paths = {a.get('outputPath') for a in artifacts if a.get('kind') == 'live-coding'}

uncovered_curated = []
for key, entry in study_topics.items():
    if entry.get('outputPath') not in study_paths:
        uncovered_curated.append({
            'key': key,
            'title': key,
            'domain': entry.get('domain', 'unknown'),
            'outputPath': entry.get('outputPath'),
            'source': 'curated',
            'tag': 'new',
        })

remaining_live = [seed for seed in live_seeds if seed.get('outputPath') not in live_paths]
remaining_live_candidates = [seed for seed in live_seed_candidates if seed.get('outputPath') not in live_paths]

recent_study_artifacts = []
for artifact in artifacts:
    if artifact.get('kind') != 'study-pack':
        continue
    try:
        ts = datetime.fromisoformat(artifact.get('updatedAt', artifact.get('createdAt')))
    except Exception:
        ts = datetime(1970, 1, 1, tzinfo=timezone.utc)
    recent_study_artifacts.append((ts, artifact))
recent_study_artifacts.sort(key=lambda x: x[0], reverse=True)

recent_domains = []
for _, artifact in recent_study_artifacts[:10]:
    path = artifact.get('outputPath', '')
    if path.startswith('database/mysql/'):
        recent_domains.append('mysql')
    elif path.startswith('database/redis/'):
        recent_domains.append('redis')
    elif path.startswith('java/spring/'):
        recent_domains.append('spring')
    elif path.startswith('java/'):
        recent_domains.append('java')
    elif path.startswith('architecture/'):
        recent_domains.append('architecture')
    elif path.startswith('search/'):
        recent_domains.append('search')
    elif path.startswith('kafka/') or path.startswith('rabbitmq/'):
        recent_domains.append('message-queue')
    elif path.startswith('interview/'):
        recent_domains.append('interview')
    else:
        recent_domains.append('other')
recent_domain_counts = Counter(recent_domains)

candidate_recommendations = []
for item in study_candidates:
    promoted_path = item.get('promotionTarget', {}).get('outputPath')
    if promoted_path and promoted_path in study_paths:
        continue
    candidate_recommendations.append(item)


def pick_recommendations():
    """ADR-010: 점수 기반 + mix target 강제.

    score = -RECENT_PENALTY_PER * recent10_domain_count
          + WEAK_AREA_BONUS (mysql/redis)
          + TAG_PRIORITY[tag]
          - CARRYOVER_PENALTY (어제 추천에 있었으면)

    1차: MIX_TARGET(new 2 / deepen 1 / review 1 / live-coding 1)을 점수 순으로 채움.
    2차: 부족하면 mix 위반 허용하고 남은 점수 상위로 채움.
    """
    yesterday_keys = load_yesterday_keys()

    pool = [dict(item) for item in candidate_recommendations]

    live_item_source = remaining_live[:3] or remaining_live_candidates[:3]
    for seed in live_item_source:
        pool.append({
            'key': f"live-coding-{seed['slug']}",
            'title': f"라이브코딩 — {seed['title']}",
            'domain': 'live-coding',
            'tag': 'live-coding',
            'difficulty': seed.get('difficulty', '중'),
            'estMinutes': 40,
            'whyNow': [
                '1차 면접 live-coding 축을 유지하기 좋다',
                '주제 풀이와 설명 연습을 같이 할 수 있다',
            ],
        })

    for item in pool:
        domain = item.get('domain', '')
        tag = item.get('tag', 'new')
        score = -RECENT_PENALTY_PER * recent_domain_counts.get(domain, 0)
        if domain in WEAK_AREAS:
            score += WEAK_AREA_BONUS
        score += TAG_PRIORITY.get(tag, -3)
        if item.get('key') in yesterday_keys:
            score -= CARRYOVER_PENALTY
        item['_score'] = score

    pool.sort(key=lambda x: -x['_score'])

    chosen = []
    used_tags = Counter()
    chosen_keys = set()

    # 1차: mix target 충족 (점수 순)
    for item in pool:
        tag = item.get('tag', 'new')
        if used_tags[tag] < MIX_TARGET.get(tag, 0):
            chosen.append(item)
            chosen_keys.add(item.get('key'))
            used_tags[tag] += 1
            if len(chosen) >= 5:
                break

    # 2차: mix 위반 허용, 점수 상위로 5개까지 채움
    if len(chosen) < 5:
        for item in pool:
            if item.get('key') in chosen_keys:
                continue
            chosen.append(item)
            chosen_keys.add(item.get('key'))
            if len(chosen) >= 5:
                break

    return chosen[:5]


recommendations = pick_recommendations()

inventory = {
    'generatedAt': datetime.now(timezone.utc).isoformat(),
    'counts': {
        'curatedStudyTopics': len(study_topics),
        'uncoveredCuratedStudyTopics': len(uncovered_curated),
        'studyTopicCandidates': len(candidate_recommendations),
        'liveCodingPrimarySeeds': len(live_seeds),
        'liveCodingRemainingPrimarySeeds': len(remaining_live),
        'liveCodingCandidateSeeds': len(live_seed_candidates),
        'liveCodingRemainingCandidateSeeds': len(remaining_live_candidates),
    },
    'recentDomainCounts': dict(recent_domain_counts),
    'pools': {
        'uncoveredCuratedStudyTopics': uncovered_curated,
        'candidateStudyTopics': candidate_recommendations,
        'remainingLiveCodingSeeds': remaining_live,
        'remainingLiveCodingCandidateSeeds': remaining_live_candidates,
    },
    'recommendations': recommendations,
}

(RUNTIME / 'topic-inventory.json').write_text(
    json.dumps(inventory, ensure_ascii=False, indent=2) + '\n',
    encoding='utf-8',
)

lines = ['오늘 추천 주제 5개', '']
for idx, item in enumerate(recommendations, start=1):
    tag_label = {'new': '신규', 'deepen': '심화', 'review': '복습'}.get(item.get('tag', 'new'), item.get('tag', 'new'))
    lines.append(f"{idx}. **{tag_label} 추천 — {item['title']}**")
    lines.append(f"   - 분야: {item.get('domain', 'unknown')}")
    lines.append(f"   - 난이도: {item.get('difficulty', '중')}")
    lines.append(f"   - 예상 학습 시간: {item.get('estMinutes', 45)}분")
    lines.append('   - 왜 지금 추천하는지')
    for reason in item.get('whyNow', []):
        lines.append(f"     - {reason}")
    lines.append('')

lines.append('재고 메모')
lines.append(f"- 신규 curated study topic 남음: {len(uncovered_curated)}개")
lines.append(f"- live-coding primary seed 남음: {len(remaining_live)}개")
lines.append(f"- live-coding candidate seed 남음: {len(remaining_live_candidates)}개")
lines.append('')
lines.append('마음에 드는 주제를 고르면 study-pack으로 바로 만들어줄게.')

(RUNTIME / 'morning-topic-recommendation.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
append_history(r.get('key') for r in recommendations if r.get('key'))
print(json.dumps({
    'inventory': str(RUNTIME / 'topic-inventory.json'),
    'recommendation': str(RUNTIME / 'morning-topic-recommendation.md'),
    'recommendationCount': len(recommendations),
    'history': str(HISTORY_PATH),
}, ensure_ascii=False))
