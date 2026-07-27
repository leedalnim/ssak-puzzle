#!/usr/bin/env python3
"""모바일 검증 — 여러 기기 뷰포트에서 레이아웃과 조작을 확인한다.

    python3 -m http.server 8123 &
    python3 tools/test_mobile.py

확인 항목: 잘림/가로스크롤 없음, 탭 이동, 스와이프 이동, 되돌리기.

주의: 이동 여부를 '남은 칸 수'로 판정하면 안 된다.
2단계 타일이 1단계로 바뀔 때는 값이 그대로라 이동을 놓친다.
진행 게이지(%)와 되돌리기 활성 여부로 판정할 것.
"""
from playwright.sync_api import sync_playwright

DEVICES = [
    ("iPhone SE",         375,  667, 2),
    ("iPhone 14",         390,  844, 3),
    ("iPhone 14 Pro Max", 430,  932, 3),
    ("Galaxy S20",        360,  800, 3),
    ("iPad mini",         768, 1024, 2),
]
# 캔버스(1024x1536) 정규화 좌표 — 스테이지1 5x5 기준
CELL_10 = (0.3757, 0.4161)   # 시작칸(0,0)의 오른쪽 칸
CELL_01 = (0.2465, 0.4950)   # 시작칸의 아래 칸


def tap_cell(pg, box, cell):
    pg.touchscreen.tap(box["x"] + box["width"] * cell[0],
                       box["y"] + box["height"] * cell[1])


with sync_playwright() as p:
    b = p.chromium.launch(
        executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
        args=["--no-sandbox"])
    for name, w, h, dsr in DEVICES:
        errs = []
        ctx = b.new_context(viewport={"width": w, "height": h},
                            device_scale_factor=dsr, is_mobile=True, has_touch=True)
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("http://localhost:8123/index.html")
        pg.wait_for_timeout(2800)
        pg.tap("#btnStart"); pg.wait_for_timeout(400)
        pg.tap("#btnIntroNext"); pg.wait_for_timeout(900)

        box = pg.query_selector("#game").bounding_box()
        # 이동 여부는 진행 게이지와 되돌리기 활성 상태로 판정한다.
        # (남은 칸 수는 2단계→1단계 변화에서 그대로라 지표로 부적합)
        prog = lambda: pg.eval_on_selector("#progressBar", "e => e.style.width")
        undoable = lambda: not pg.is_disabled("#btnUndo")
        t0 = prog()

        # 1) 인접 칸 탭
        tap_cell(pg, box, CELL_10); pg.wait_for_timeout(450)
        t1 = prog(); u1 = undoable()

        # 2) 스와이프(아래로)
        cx = box["x"] + box["width"] * 0.5
        cy = box["y"] + box["height"] * 0.5
        pg.touchscreen.tap(cx, cy)          # 포커스
        pg.wait_for_timeout(150)
        pg.mouse.move(cx, cy)
        pg.touchscreen.tap(cx, cy)
        # Playwright touchscreen엔 swipe가 없어 CDP 대신 수동 dispatch
        pg.evaluate("""([x, y]) => {
          const cv = document.querySelector('#game');
          const mk = (type, cx, cy) => {
            const t = new Touch({identifier: 1, target: cv, clientX: cx, clientY: cy});
            return new TouchEvent(type, {touches: type === 'touchend' ? [] : [t],
                                         changedTouches: [t], bubbles: true, cancelable: true});
          };
          cv.dispatchEvent(mk('touchstart', x, y));
          cv.dispatchEvent(mk('touchmove', x, y + 60));
          cv.dispatchEvent(mk('touchend', x, y + 60));
        }""", [cx, cy])
        pg.wait_for_timeout(450)
        t2 = prog()

        # 3) 되돌리기 버튼
        pg.tap("#btnUndo"); pg.wait_for_timeout(400)
        t3 = prog()

        # 레이아웃
        m = pg.evaluate("""() => {
          const q = s => document.querySelector(s).getBoundingClientRect();
          const hud = q('#hud'), tb = q('#toolbar');
          return {vh: innerHeight, hudTop: Math.round(hud.top),
                  barBottom: Math.round(tb.bottom),
                  ox: document.documentElement.scrollWidth > innerWidth};
        }""")
        clipped = m['hudTop'] < 0 or m['barBottom'] > m['vh'] + 1

        print(f"{name:18s} {w}x{h}")
        print(f"   레이아웃 {'✅ 정상' if not clipped and not m['ox'] else '❌ 잘림/스크롤'}")
        print(f"   탭 이동   진행 {t0}→{t1}, undo활성={u1} {'✅' if t1 != t0 else '❌'}")
        print(f"   스와이프  진행 {t1}→{t2} {'✅' if t2 != t1 else '❌'}")
        print(f"   되돌리기  진행 {t2}→{t3} {'✅' if t3 != t2 else '❌'}")
        if errs:
            print("   에러:", errs[:2])
        pg.screenshot(path=f"/tmp/m_{name.replace(' ', '_')}.png")
        ctx.close()
    b.close()
