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

# ------------------------------- 수집품 조각 배치 -------------------------------
# 물건은 **조각**을 모아야 해금된다. 조각 수는 물건마다 1~5개.
# 한 판에 여러 개가 흩뿌려지고, 뒤로 갈수록 개수가 늘어난다.
# 한붓그리기라 모든 칸을 반드시 밟으므로 **놓칠 수 있는 조각은 없다**.
NEEDS = {
    '구겨진 잠옷': 1,
    '머그컵': 2, '티슈 상자': 2,
    '노란 고무장갑': 3, '분무기': 3, '쿠션': 3,
    '탁상 램프': 4, '작은 화분': 4, '물뿌리개': 4,
    '장바구니': 5, '새 운동화': 5,
}   # 합계 36조각

# 판마다 떨어지는 조각 — 이야기 순서(잠옷 → 운동화)대로 해금되도록 짠 표.
# 개수 곡선: 1~8판 1개, 9~15판 2개, 16~19판 3개, 마지막 20판은 2개.
# 8 + 14 + 12 + 2 = 36 으로 NEEDS 합계와 정확히 맞아, 20판을 다 깨면 11종이 전부 열린다.
# 해금 시점: 1·3·5·8·11·13·14·16·19·20·20판.
DROPS = [
    ['구겨진 잠옷'],                              # 1  ← 잠옷 해금
    ['머그컵'],                                   # 2
    ['머그컵'],                                   # 3  ← 머그컵
    ['티슈 상자'],                                # 4
    ['티슈 상자'],                                # 5  ← 티슈 상자
    ['노란 고무장갑'],                            # 6
    ['노란 고무장갑'],                            # 7
    ['노란 고무장갑'],                            # 8  ← 고무장갑
    ['분무기', '탁상 램프'],                      # 9
    ['분무기', '탁상 램프'],                      # 10
    ['분무기', '쿠션'],                           # 11 ← 분무기
    ['쿠션', '탁상 램프'],                        # 12
    ['쿠션', '작은 화분'],                        # 13 ← 쿠션
    ['탁상 램프', '작은 화분'],                   # 14 ← 탁상 램프
    ['작은 화분', '물뿌리개'],                    # 15
    ['작은 화분', '장바구니', '새 운동화'],       # 16 ← 작은 화분
    ['물뿌리개', '장바구니', '새 운동화'],        # 17
    ['물뿌리개', '장바구니', '새 운동화'],        # 18
    ['물뿌리개', '장바구니', '새 운동화'],        # 19 ← 물뿌리개
    ['장바구니', '새 운동화'],                    # 20 ← 장바구니 · 새 운동화
]


def check_drops():
    """배치표가 NEEDS 와 정확히 맞는지 — 어긋나면 영영 못 여는 물건이 생긴다."""
    got = {}
    for i, names in enumerate(DROPS, 1):
        if len(set(names)) != len(names):
            raise RuntimeError(f'{i}판에 같은 물건이 두 번 들어갔다')
        for nm in names:
            if nm not in NEEDS:
                raise RuntimeError(f'{i}판: 모르는 물건 {nm}')
            got[nm] = got.get(nm, 0) + 1
    if got != NEEDS:
        diff = {k: (got.get(k, 0), v) for k, v in NEEDS.items() if got.get(k, 0) != v}
        raise RuntimeError(f'조각 수 불일치(실제, 필요): {diff}')
    return sum(NEEDS.values())


def item_spots(n, obstacles, path, i, count):
    """수집품이 놓일 칸들 — 시작칸·장애물을 피하고, 경로에서 **늦게** 밟는 칸을 고른다.
       (바로 먹어버리면 '찾았다'는 맛이 없다)
       여러 개일 때는 서로 붙지 않도록 한 칸 이상 띄운다."""
    obs = {(o['x'], o['y']) for o in obstacles}
    first = {}
    for k, c in enumerate(path):
        if c not in first:
            first[c] = k                       # 각 칸을 처음 밟는 시점
    cand = [c for c in first if c not in obs and c != (0, 0)]
    cand.sort(key=lambda c: -first[c])          # 늦게 밟는 순
    if not cand:
        return []
    # 판마다 다른 자리에서 시작해 같은 구석에만 몰리지 않게 한다
    off = i % max(1, min(4, len(cand)))
    cand = cand[off:] + cand[:off]
    picked = []
    for gap in (2, 1, 0):                       # 되도록 띄우되, 안 되면 조건을 푼다
        for c in cand:
            if len(picked) >= count:
                break
            if all(max(abs(c[0] - p[0]), abs(c[1] - p[1])) >= gap for p in picked):
                picked.append(c)
        if len(picked) >= count:
            break
    return [{'x': x, 'y': y} for x, y in picked[:count]]


if __name__ == '__main__':
    total_pieces = check_drops()
    print(f"  조각 배치표 OK — {len(NEEDS)}종 / 총 {total_pieces}조각", file=sys.stderr)
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
        drops = DROPS[i - 1]             # 이 판에 흩뿌려지는 조각들
        solutions[i] = [list(p) for p in path]
        st = {
            'id': i, 'act': 1, 'place': '자취방', 'sub': i, 'theme': theme, 'bg': 'studio',
            'grid': grid, 'start': {'x': 0, 'y': 0}, 'time': time_limit,
            'intro': intro, 'clear': clear, 'unlocks': drops, 'obstacles': obstacles,
        }
        # 조각은 바닥에 흩뿌려 둔다(지나가면 줍는다). 자리가 모자라면 그만큼만.
        spots = item_spots(n, obstacles, path, i, len(drops))
        if len(spots) < len(drops):
            raise RuntimeError(f'스테이지 {i}: 조각 {len(drops)}개를 놓을 자리가 없다')
        st['items'] = [{'name': nm, **sp} for nm, sp in zip(drops, spots)]
        stages.append(st)
    with open('stages/solutions.json', 'w', encoding='utf-8') as f:
        json.dump(solutions, f, ensure_ascii=False)
    # 해금에 필요한 조각 수는 여기(NEEDS)가 원본 — 게임은 이 파일을 읽어 쓴다
    with open('stages/items.json', 'w', encoding='utf-8') as f:
        json.dump(NEEDS, f, ensure_ascii=False, indent=2)
    json.dump(stages, sys.stdout, ensure_ascii=False, indent=2)
