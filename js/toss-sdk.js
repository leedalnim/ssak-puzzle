// 앱인토스 SDK 래퍼 (스텁).
// 실제 출시 시 @apps-in-toss SDK 로 교체. 지금은 웹에서도 동작하도록 더미 구현.
// 참고: https://developers-apps-in-toss.toss.im/llms.txt

const KEY = 'ssak_user_key';

export const Toss = {
  ready: false,

  async init() {
    // 실제: const { userKey } = await appLogin();  등
    this.ready = true;
    let uk = localStorage.getItem(KEY);
    if (!uk) { uk = 'guest_' + Math.random().toString(36).slice(2, 10); localStorage.setItem(KEY, uk); }
    this.userKey = uk;
    return uk;
  },

  // 보상형 광고 — 성공 시 resolve(true)
  async showRewardedAd() {
    // 실제: AdMob 보상형 광고 호출
    // 더미: 잠깐 대기 후 보상 지급
    return new Promise((res) => setTimeout(() => res(true), 600));
  },

  track(event, props = {}) {
    // 실제: 앱인토스 이벤트 트래킹
    if (window.__SSAK_DEBUG) console.log('[track]', event, props);
  },

  // 미니앱 닫기
  close() {
    // 실제: 앱인토스 close API
    if (this.onClose) this.onClose();
  },
};
