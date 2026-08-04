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


TYPES = ['basket_rd', 'plant', 'books']

# 장애물 배치 후보 — 시작칸(0,0)은 절대 막지 않고, 보드가 끊기지 않는 자리만.
# 판마다 다른 조합을 써서 같은 5×5라도 매번 다른 문제로 느껴지게 한다.
SPOTS = {
    1: [[(4, 0)], [(0, 4)], [(4, 4)], [(2, 2)]],
    2: [[(4, 0), (0, 4)], [(4, 4), (2, 2)], [(4, 0), (4, 4)], [(0, 4), (2, 2)]],
    3: [[(4, 0), (0, 4), (2, 2)], [(4, 0), (4, 4), (0, 4)],
        [(4, 0), (2, 2), (4, 4)], [(0, 4), (2, 2), (2, 0)]],
    4: [[(4, 0), (0, 4), (2, 2), (4, 4)], [(4, 0), (2, 0), (0, 4), (2, 2)],
        [(0, 4), (4, 4), (2, 2), (4, 0)], [(4, 0), (4, 4), (2, 2), (0, 4)]],
}


def obstacles_for(count, i):
    if count == 0:
        return []
    variant = SPOTS[count][(i - 1) % len(SPOTS[count])]
    return [{'x': x, 'y': y, 'type': TYPES[k % len(TYPES)]}
            for k, (x, y) in enumerate(variant)]


# 20판 난이도 스케줄 — **격자는 5×5 고정**.
# 난이도는 (1) 때 단계가 깊어지고 (2) 장애물이 늘고 (3) 뒤로 갈수록 제한시간이 붙는다.
# 격자 확대는 다음 장소(편의점 등)에서 쓴다.
def schedule(i):  # i: 1..20 → (격자, 최대더러움, 장애물수, 제한시간[0=무제한])
    if i <= 3:   return 5, 2, 0, 0          # 조작 익히기
    if i <= 6:   return 5, 2, 1, 0          # 장애물 등장
    if i <= 9:   return 5, 3, 1, 0          # 때가 깊어짐
    if i <= 12:  return 5, 3, 2, 0          # 장애물 둘
    if i <= 15:  return 5, 3, 2, 200        # 시간 압박 시작
    if i <= 18:  return 5, 4, 3, 190        # 장애물 셋 + 더 깊은 때
    return 5, 4, 4, 175                     # 마지막 관문

# 스토리(자취방) — 일부 판에만
STORY = {
    1:  ('내 방', '눈을 떴다.\n며칠을 누워만 있었더라.\n\n…일단, 발밑부터 닦아볼까.',
         '방바닥이 보인다.\n별거 아닌데, 조금 개운하다.'),
    2:  ('침대 옆', '', '쌓아둔 컵라면 그릇을 치웠다.\n손이 제법 움직인다.'),
    5:  ('쌓인 빨래', '찌든 얼룩은 한 번에 안 지워진다.\n같은 자리를 여러 번 쓱— 쓱—.',
         '두 번, 세 번 문지르니 결국 깨끗해진다.'),
    10: ('창가 정리', '', '햇살이 드는 창가.\n먼지 한 톨 없이 닦아냈다.'),
    15: ('책상 밑', '', '미뤄둔 구석까지 손이 닿는다.'),
    20: ('방 한 칸, 끝', '마지막 한 칸.', '방이 반짝인다.\n그러고 보니… 나, 조금 움직이고 있구나.'),
}

# 판마다 하나씩 수집품 **조각**이 나온다. 종류는 11가지라 뒤쪽 판에서 다시 나오고,
# 조각이 필요 수(js/main.js 의 need)만큼 모이면 수집함에서 해금된다.
# 잠옷·운동화는 1조각, 나머지 9종은 2조각 → 1 + 9×2 + 1 = 20판과 정확히 맞는다.
# 이야기 순서대로 — 잠옷으로 시작해 운동화(=밖으로 나갈 준비)로 끝난다.
UNLOCKS = [
    '구겨진 잠옷',   # 1
    '머그컵',        # 2
    '티슈 상자',     # 3
    '노란 고무장갑', # 4
    '분무기',        # 5
    '쿠션',          # 6
    '탁상 램프',     # 7
    '작은 화분',     # 8
    '물뿌리개',      # 9
    '장바구니',      # 10
    '새 운동화',     # 11  ← 11종 한 바퀴
    '머그컵',        # 12  ↓ 여기부터는 같은 물건이 하나 더
    '노란 고무장갑', # 13
    '티슈 상자',     # 14
    '작은 화분',     # 15
    '분무기',        # 16
    '쿠션',          # 17
    '탁상 램프',     # 18
    '물뿌리개',      # 19
    '장바구니',      # 20
]

def item_spot(n, obstacles, path, i):
    """수집품이 놓일 칸 — 시작칸·장애물을 피하고, 경로에서 **늦게** 밟는 칸으로 고른다.
       (바로 먹어버리면 '찾았다'는 맛이 없다)"""
    obs = {(o['x'], o['y']) for o in obstacles}
    first = {}
    for k, c in enumerate(path):
        if c not in first:
            first[c] = k                       # 각 칸을 처음 밟는 시점
    cand = [c for c in first if c not in obs and c != (0, 0)]
    if not cand:
        return None
    cand.sort(key=lambda c: -first[c])          # 늦게 밟는 순
    x, y = cand[i % max(1, min(4, len(cand)))]  # 상위 몇 개 중 판마다 다르게
    return {'x': x, 'y': y}


if __name__ == '__main__':
    stages, solutions = [], {}
    for i in range(1, 21):
        n, max_dur, ocount, time_limit = schedule(i)
        obstacles = obstacles_for(ocount, i)
        grid, path = build(n, obstacles, max_dur, seed=i * 37 + 3)
        ok, msg = replay_ok(grid, obstacles, {'x': 0, 'y': 0}, path)
        print(f"  [{i:2d}] 자취방 {n}x{n} d{max_dur} obs{ocount} t{time_limit} — {msg}", file=sys.stderr)
        if not ok:
            raise RuntimeError(f'스테이지 {i} 검증 실패: {msg}')
        theme, intro, clear = STORY.get(i, (f'{i}번째 칸', '', ''))
        unlock = UNLOCKS[i - 1]          # 모든 판에서 수집품이 하나씩 나온다
        solutions[i] = [list(p) for p in path]
        st = {
            'id': i, 'act': 1, 'place': '자취방', 'sub': i, 'theme': theme, 'bg': 'studio',
            'grid': grid, 'start': {'x': 0, 'y': 0}, 'time': time_limit,
            'intro': intro, 'clear': clear, 'unlock': unlock, 'obstacles': obstacles,
        }
        # 해금 아이템이 있는 판은 바닥에 그 물건을 떨어뜨려 둔다(지나가면 줍는다)
        if unlock:
            spot = item_spot(n, obstacles, path, i)
            if spot:
                st['item'] = {'name': unlock, **spot}
        stages.append(st)
    with open('stages/solutions.json', 'w', encoding='utf-8') as f:
        json.dump(solutions, f, ensure_ascii=False)
    json.dump(stages, sys.stdout, ensure_ascii=False, indent=2)
