#!/usr/bin/env python3
"""스테이지 격자 생성기.

무작위 배치 후 솔버로 거르는 방식은 격자가 커지면 사실상 못 찾는다
(한붓그리기는 체스판 패리티 제약이 강해 대부분의 배치가 풀리지 않음).

대신 **경로를 먼저 만들고 방문 횟수를 더러움으로 삼는다.**
그 경로를 그대로 재생하면 클리어되므로 풀림이 구성적으로 보장된다.

    python3 tools/gen_stages.py > stages/stages.json
"""
import json, random, sys

DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def make_grid(n, obstacles, max_dur, rnd, start=(0, 0)):
    """모든 칸을 덮는 임의 보행을 만들고 (방문횟수, 보행경로)를 반환."""
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
                # 아직 안 밟은 칸을 우선 — 커버리지를 빨리 채운다
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
        grid[y][x] = 1          # 데이터상 값은 두되 통행은 obstacles로 막는다
    return grid, path


def build(n, obstacles, max_dur, seed):
    rnd = random.Random(seed)
    for _ in range(400):
        g, path = make_grid(n, obstacles, max_dur, rnd)
        if g:
            return g, path
    raise RuntimeError(f'{n}x{n} 생성 실패')


def replay_ok(grid, obstacles, start, path):
    """생성 경로를 그대로 재생해 실제로 클리어되는지 확인 (O(n), 즉시)."""
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


# 장소마다 5×5 → 6×6 → 7×7 로 커진다
PLACES = [
    ('자취방', 'studio', [
        ('내 방', '눈을 떴다.\n며칠을 누워만 있었더라.\n\n…일단, 발밑부터 닦아볼까.',
         '방바닥이 보인다.\n별거 아닌데, 조금 개운하다.', '구겨진 잠옷'),
        ('침대 옆', '', '쌓아둔 컵라면 그릇을 치웠다.\n손이 제법 움직인다.', ''),
        ('쌓인 빨래', '찌든 얼룩은 한 번에 안 지워진다.\n같은 자리를 여러 번 쓱— 쓱—.',
         '두 번, 세 번 문지르니 결국 깨끗해진다.\n포기 안 하면 되는 거였네.', '노란 고무장갑'),
    ]),
    ('편의점', 'studio', [
        ('편의점 첫날', '첫 알바, 편의점.\n"바닥 좀 밀어줄래요?"\n\n걸레질이라면… 자신 있는데?',
         '사장님이 엄지를 척.\n시급보다 그 한마디가 더 좋았다.', '편의점 유니폼'),
        ('진열대 사이', '', '좁은 통로도 요령이 생겼다.', ''),
        ('마감 청소', '', '문 닫고 혼자 하는 마감.\n이 시간이 싫지만은 않다.', '운동화'),
    ]),
    ('카페', 'studio', [
        ('카페 오픈', '', '원두 향이 밴 마룻바닥.\n사람들 사이에 있는 게 나쁘지 않다.', '바리스타 앞치마'),
        ('테이블 사이', '', '손님이 남긴 자리를 정리했다.', ''),
        ('마감 후', '', '의자를 올리고 마지막으로 한 바퀴.', ''),
    ]),
    ('베이커리', 'studio', [
        ('오픈 전', '오픈 전 베이커리 대청소.\n밀가루가 잔뜩 내려앉았다.\n\n오늘도 쓱— 싹—.',
         '갓 구운 빵 냄새, 반짝이는 매장.', ''),
        ('작업대 아래', '', '구석까지 손이 닿는다.', ''),
        ('마지막 밤', '', '그러고 보니… 나, 꽤 멀리 왔구나.', '제빵사 모자'),
    ]),
]

SIZES = [
    (5, 2, 0,   [{'x': 4, 'y': 0, 'type': 'basket_rd'}]),
    (6, 2, 150, [{'x': 5, 'y': 0, 'type': 'basket_rd'}, {'x': 0, 'y': 5, 'type': 'plant'}]),
    (7, 3, 180, [{'x': 6, 'y': 0, 'type': 'basket_rd'}, {'x': 0, 'y': 6, 'type': 'plant'},
                 {'x': 3, 'y': 3, 'type': 'stool'}]),
]

if __name__ == '__main__':
    stages, sid, solutions = [], 0, {}
    for act, (place, bg, chapters) in enumerate(PLACES, start=1):
        for i, (theme, intro, clear, unlock) in enumerate(chapters):
            n, max_dur, time_limit, obstacles = SIZES[i]
            sid += 1
            grid, path = build(n, obstacles, max_dur, seed=sid * 17)
            ok, msg = replay_ok(grid, obstacles, {'x': 0, 'y': 0}, path)
            print(f"  [{sid:2d}] {place} {theme} {n}x{n} — {msg}", file=sys.stderr)
            if not ok:
                raise RuntimeError(f'스테이지 {sid} 검증 실패: {msg}')
            solutions[sid] = [list(p) for p in path]
            stages.append({
                'id': sid, 'act': act, 'place': place, 'theme': theme, 'bg': bg,
                'grid': grid,
                'start': {'x': 0, 'y': 0},
                'time': time_limit,
                'intro': intro, 'clear': clear, 'unlock': unlock,
                'obstacles': obstacles,
            })
    with open('stages/solutions.json', 'w', encoding='utf-8') as f:
        json.dump(solutions, f, ensure_ascii=False)
    json.dump(stages, sys.stdout, ensure_ascii=False, indent=2)
