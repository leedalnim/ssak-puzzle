# 🎮 슥삭퍼즐 (Ssak-Ssak Puzzle)

한붓 그리기 × 청소 퍼즐. 무기력하게 쓰레기집에 살던 청년이 방 한 칸을 닦는 것을
계기로, 다양한 알바에 도전하며 다시 세상 밖으로 나아가는 이야기.

> 기획안 기반 플레이 가능한 MVP. HTML5 Canvas + Vanilla JS (앱인토스 이식 친화 구조).
> **그래픽 우선** — 코지 픽셀아트, 성장 그라데이션, 먼지·반짝임 파티클, 콤보 사운드.

## 플레이 방법

정적 파일이라 서버 하나면 됩니다 (ES module + fetch 때문에 `file://` 직접 열기는 불가):

```bash
python3 -m http.server 8000
# 브라우저에서 http://localhost:8000
```

- **이동**: 방향키 / WASD / 스와이프 / 캐릭터 인접 타일 터치
- **규칙**: 지나간 타일은 닦이고(내구도 -1), 0이 되면 더는 못 지나감(완성된 선).
  노란칸=3번, 파란칸=2번, 회색칸=1번 지나가야 깨끗. 모든 칸을 닦으면 클리어.
- **되돌리기(↩) / 다시(⟳)** 버튼으로 부담 없이 재시도.

## 구조

```
index.html            진입점 + UI 오버레이(타이틀/스테이지/모달)
css/style.css         코지 UI, 픽셀 렌더링, Safe Area 대응
js/
  main.js             부트스트랩 + 화면 상태기계 + 진행 저장
  game.js             퍼즐 로직 + 캔버스 렌더러(트윈/파티클/성장 그라데이션)
  assets.js           PNG 스프라이트 로더
  audio.js            WebAudio 절차적 효과음(슥삭/콤보/클리어)
  particles.js        먼지·반짝임·색종이 파티클
  input.js            키보드 / 스와이프 / 인접 터치
  toss-sdk.js         앱인토스 SDK 래퍼(스텁) — 출시 시 교체
stages/
  stages.json         스테이지 데이터(그리드/시작/서사/무드 색)
  solutions.json      검증된 해답(힌트용, 자동 생성)
assets/*.png          스프라이트(생성물)
tools/
  gen_assets.py       픽셀아트 에셋 생성기(에셋 원본)
  solve.py            한붓 청소 솔버 / 스테이지 풀이 검증
  preview_scene.py    렌더러를 흉내 낸 게임 화면 미리보기(브라우저 없이 확인)
  test_game.mjs       실제 game.js 로직 런타임 테스트
```

## 에셋 / 검증 워크플로우

```bash
python3 tools/gen_assets.py preview   # 스프라이트 생성 + 미리보기(tools/_preview.png)
python3 tools/preview_scene.py        # 실제 게임 화면 합성(tools/_scene.png)
python3 tools/solve.py                # 모든 스테이지 풀이 가능 검증 + 해답 생성
node    tools/test_game.mjs           # game.js 로직으로 8스테이지 클리어 확인
```

## 그래픽 방향(중요)

에셋은 모두 교체 가능한 PNG. 더 높은 퀄리티를 위해 ① AI 생성(힉스필드 등),
② 무료 픽셀 에셋 팩 → 같은 규격(타일 16×16, 캐릭터 16×24)으로 끼워 넣으면 됩니다.
색 팔레트·무드는 `tools/gen_assets.py` 와 `stages.json` 의 `moodFrom/moodTo` 로 조정.

## 앱인토스(나중에)

`js/toss-sdk.js` 스텁을 실제 SDK(로그인/유저키/AdMob 보상형 광고/이벤트 트래킹)로
교체하면 됩니다. 게임 로직과 분리돼 있어 완성 후 붙여도 무방.

## 실행

```bash
python3 -m http.server 8000
# http://localhost:8000
```

## 구조 (v2 — 코지룸 3D 클레이)

```
js/render.js   방 씬 렌더러. 보드를 평면에서 통짜 조립 후 1회 원근 변형(호모그래피)
js/game.js     퍼즐 로직 + 캔버스 렌더 호출
js/main.js     화면 상태기계(타이틀/인트로/게임/클리어/실패/도움말/일시정지)
css/style.css  UI. HUD·툴바는 앵커 기준 배치, --k 배율로 캔버스와 동기화
assets/room/   배경·타일6·캐릭터12·장애물6·UI6
```

렌더링·에셋 규칙은 [`CONCEPT.md`](CONCEPT.md) 참조.
