#!/usr/bin/env python3
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

TASK_ROOT = Path.home() / 'ai-nodes' / 'career-os'
CONFIG = TASK_ROOT / 'config'
RUNTIME = TASK_ROOT / 'data' / 'runtime'
RUNTIME.mkdir(parents=True, exist_ok=True)


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def sort_key(item):
    return (
        {'new': 0, 'deepen': 1, 'review': 2}.get(item.get('tag'), 9),
        item.get('domain', 'zzz'),
        item.get('title', 'zzz'),
    )


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
    chosen = []
    used_domains = Counter()
    target_order = ['database', 'architecture', 'spring', 'message-queue', 'search', 'redis', 'interview']
    pool = sorted(candidate_recommendations, key=sort_key)

    live_item_source = remaining_live[:1] or remaining_live_candidates[:1]
    for seed in live_item_source:
        pool.append({
            'key': f"live-coding-{seed['slug']}",
            'title': f"라이브코딩 — {seed['title']}",
            'domain': 'live-coding',
            'tag': 'new',
            'difficulty': seed.get('difficulty', '중'),
            'estMinutes': 40,
            'whyNow': [
                '1차 면접 live-coding 축을 유지하기 좋다',
                '주제 풀이와 설명 연습을 같이 할 수 있다',
            ],
        })

    def already(key):
        return any(existing.get('key') == key for existing in chosen)

    for target in target_order:
        if len(chosen) >= 5:
            break
        for item in pool:
            key = item.get('key')
            domain = item.get('domain')
            if already(key):
                continue
            if domain == target and used_domains[domain] == 0:
                chosen.append(item)
                used_domains[domain] += 1
                break

    for item in pool:
        if len(chosen) >= 5:
            break
        key = item.get('key')
        domain = item.get('domain')
        if already(key):
            continue
        if used_domains[domain] == 0 or recent_domain_counts.get(domain, 0) == 0:
            chosen.append(item)
            used_domains[domain] += 1

    for item in pool:
        if len(chosen) >= 5:
            break
        key = item.get('key')
        domain = item.get('domain')
        if already(key):
            continue
        chosen.append(item)
        used_domains[domain] += 1

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
print(json.dumps({
    'inventory': str(RUNTIME / 'topic-inventory.json'),
    'recommendation': str(RUNTIME / 'morning-topic-recommendation.md'),
    'recommendationCount': len(recommendations),
}, ensure_ascii=False))
