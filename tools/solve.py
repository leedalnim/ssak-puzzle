#!/usr/bin/env python3
"""
한붓 청소 퍼즐 솔버 / 검증기.

규칙:
- grid[y][x]: 0=벽(빈칸), 1/2/3=내구도(지나가야 하는 횟수)
- 캐릭터는 상하좌우 인접 칸으로 이동. 내구도>0 인 칸으로만 진입 가능.
- 진입 시 그 칸 내구도 -1. 0이 되면 '청소완료' → 더는 진입 불가.
- 시작 칸은 시작 시 -1.
- 모든 칸 내구도 0 = 클리어.

사용:
  python3 tools/solve.py            # stages/stages.json 전체 검증
  (개발 중 후보 레이아웃은 CANDIDATES 에서 바로 테스트)
"""
import json, os, sys

def solve(grid, start, node_cap=4_000_000):
    H = len(grid); W = len(grid[0])
    dur = [row[:] for row in grid]
    sx, sy = start['x'], start['y']
    if dur[sy][sx] <= 0:
        return None
    dur[sy][sx] -= 1
    total = sum(v for row in grid for v in row)  # 총 닦아야 하는 횟수
    # 이미 시작칸 1회 소비
    remaining_moves = total - 1
    path = []
    seen = set()
    nodes = [0]
    sys.setrecursionlimit(100000)

    def key(x, y):
        return (x, y, tuple(tuple(r) for r in dur))

    def all_clean():
        return all(v == 0 for row in dur for v in row)

    def dfs(x, y, left):
        if all_clean():
            return True
        nodes[0] += 1
        if nodes[0] > node_cap:
            return False
        k = key(x, y)
        if k in seen:
            return False
        seen.add(k)
        for dx, dy, name in ((0, -1, 'up'), (0, 1, 'down'), (-1, 0, 'left'), (1, 0, 'right')):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and dur[ny][nx] > 0:
                dur[ny][nx] -= 1
                path.append(name)
                if dfs(nx, ny, left - 1):
                    return True
                path.pop()
                dur[ny][nx] += 1
        return False

    ok = dfs(sx, sy, remaining_moves)
    return path if ok else None


def check_stage(st):
    # 장애물이 놓인 칸은 통행 불가 — 게임 로직과 동일하게 0으로 막고 푼다
    grid = [row[:] for row in st['grid']]
    for o in st.get('obstacles', []):
        grid[o['y']][o['x']] = 0
    sol = solve(grid, st['start'])
    name = f"#{st.get('id','?')} {st.get('theme','')}"
    if sol is None:
        print(f"  ✗ {name}: 풀 수 없음!")
        return False, None
    print(f"  ✓ {name}: 해법 {len(sol)}수")
    return True, sol


# 개발 중 후보 레이아웃 빠른 테스트용
CANDIDATES = {
    'plus3': {'id': 'c', 'theme': 'plus3', 'grid': [
        [0, 1, 0],
        [1, 3, 1],
        [0, 1, 0],
    ], 'start': {'x': 1, 'y': 0}},
}

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'cand':
        for k, st in CANDIDATES.items():
            check_stage(st)
        sys.exit(0)
    path = os.path.join(os.path.dirname(__file__), '..', 'stages', 'stages.json')
    with open(path, encoding='utf-8') as f:
        stages = json.load(f)
    print(f"스테이지 {len(stages)}개 검증:")
    allok = True
    sols = {}
    for st in stages:
        ok, sol = check_stage(st)
        allok = allok and ok
        if sol is not None:
            sols[st['id']] = sol
    # 해법을 hints 파일로 저장(힌트 기능용)
    out = os.path.join(os.path.dirname(__file__), '..', 'stages', 'solutions.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(sols, f, ensure_ascii=False, indent=1)
    print("solutions.json 저장:", out)
    sys.exit(0 if allok else 1)
