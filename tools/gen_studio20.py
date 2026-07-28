#!/usr/bin/env python3
"""자취방 20판 생성 — 난이도 곡선(5×5→7×7, 더러움·장애물·시간 점증).

경로를 먼저 만들고 방문 횟수를 더러움으로 삼는 방식(구성적 풀림 보장)을 재사용.

    python3 tools/gen_studio20.py > stages/stages.json
"""
import json, random, sys

DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def make_grid(n, obstacles, max_dur, rnd, start=(0, 0)):
    obs = {(o['x'], o['y']) for o in obstacles}
    cells = [(x, y) for y in range(n) for x in range(n) if (x, y) not in obs]
    visits = {c: 0 for c in cells}
    cur = start
    visits[cur] = 1
    path = [cur]
    guard = 0
    while min(visits.values()) == 0 and guard < 200000:
        guard += 1
        cand = []
        for dx, dy in DIRS:
            nxt = (cur[0] + dx, cur[1] + dy)
            if nxt in visits and visits[nxt] < max_dur:
                cand += [nxt] * (6 if visits[nxt] == 0 else 1)
        if not cand:
            break
        cur = rnd.choice(cand)
        visits[cur] += 1
        path.append(cur)
    if min(visits.values()) == 0:
        return None, None
    grid = [[0] * n for _ in range(n)]
    for (x, y), v in visits.items():
        grid[y][x] = v
    for (x, y) in obs:
        grid[y][x] = 1
    return grid, path


def build(n, obstacles, max_dur, seed):
    rnd = random.Random(seed)
    for _ in range(800):
        g, path = make_grid(n, obstacles, max_dur, rnd)
        if g:
            return g, path
    raise RuntimeError(f'{n}x{n} 생성 실패')


def replay_ok(grid, obstacles, start, path):
    dur = [row[:] for row in grid]
    for o in obstacles:
        dur[o['y']][o['x']] = 0
    if path[0] != (start['x'], start['y']):
        return False, '시작 위치 불일치'
    dur[path[0][1]][path[0][0]] -= 1
    for i in range(1, len(path)):
        (px, py), (x, y) = path[i - 1], path[i]
        if abs(px - x) + abs(py - y) != 1:
            return False, f'{i}수: 인접하지 않은 이동'
        if dur[y][x] <= 0:
            return False, f'{i}수: 이미 깨끗한 칸 진입'
        dur[y][x] -= 1
    left = sum(v for row in dur for v in row)
    return left == 0, ('클리어' if left == 0 else f'{left}회 남음')


def obstacles_for(n, count):
    """격자 크기에 맞춰 모서리 위주로 장애물 배치 (사용 에셋: basket_rd·plant·books)."""
    pool = [
        {'x': n - 1, 'y': 0, 'type': 'basket_rd'},
        {'x': 0, 'y': n - 1, 'type': 'plant'},
        {'x': n // 2, 'y': n // 2, 'type': 'books'},
    ]
    return pool[:count]


# 20판 난이도 스케줄: (격자, 최대더러움, 장애물수, 제한시간[0=무제한])
def schedule(i):  # i: 1..20
    if i <= 4:      # 튜토리얼
        return 5, 2, (0 if i <= 2 else 1), 0
    if i <= 9:      # 초급
        return (5 if i <= 6 else 6), (2 if i <= 6 else 3), 1, 0
    if i <= 14:     # 중급
        return 6, 3, 2, (0 if i <= 11 else 210)
    return 7, (3 if i <= 17 else 4), 3, 200  # 고급

# 스토리(자취방) — 일부 판에만
STORY = {
    1:  ('내 방', '눈을 떴다.\n며칠을 누워만 있었더라.\n\n…일단, 발밑부터 닦아볼까.',
         '방바닥이 보인다.\n별거 아닌데, 조금 개운하다.', '구겨진 잠옷'),
    2:  ('침대 옆', '', '쌓아둔 컵라면 그릇을 치웠다.\n손이 제법 움직인다.', ''),
    5:  ('쌓인 빨래', '찌든 얼룩은 한 번에 안 지워진다.\n같은 자리를 여러 번 슥— 슥—.',
         '두 번, 세 번 문지르니 결국 깨끗해진다.', '노란 고무장갑'),
    10: ('창가 정리', '', '햇살이 드는 창가.\n먼지 한 톨 없이 닦아냈다.', ''),
    15: ('책상 밑', '', '미뤄둔 구석까지 손이 닿는다.', '작은 화분'),
    20: ('방 한 칸, 끝', '마지막 한 칸.', '방이 반짝인다.\n그러고 보니… 나, 조금 움직이고 있구나.', '새 운동화'),
}

if __name__ == '__main__':
    stages, solutions = [], {}
    for i in range(1, 21):
        n, max_dur, ocount, time_limit = schedule(i)
        obstacles = obstacles_for(n, ocount)
        grid, path = build(n, obstacles, max_dur, seed=i * 37 + 3)
        ok, msg = replay_ok(grid, obstacles, {'x': 0, 'y': 0}, path)
        print(f"  [{i:2d}] 자취방 {n}x{n} d{max_dur} obs{ocount} t{time_limit} — {msg}", file=sys.stderr)
        if not ok:
            raise RuntimeError(f'스테이지 {i} 검증 실패: {msg}')
        theme, intro, clear, unlock = STORY.get(i, (f'{i}번째 칸', '', '', ''))
        solutions[i] = [list(p) for p in path]
        stages.append({
            'id': i, 'act': 1, 'place': '자취방', 'sub': i, 'theme': theme, 'bg': 'studio',
            'grid': grid, 'start': {'x': 0, 'y': 0}, 'time': time_limit,
            'intro': intro, 'clear': clear, 'unlock': unlock, 'obstacles': obstacles,
        })
    with open('stages/solutions.json', 'w', encoding='utf-8') as f:
        json.dump(solutions, f, ensure_ascii=False)
    json.dump(stages, sys.stdout, ensure_ascii=False, indent=2)
