function loadContent(path, clicked) {
  const iframe = document.getElementById('content-frame');

  // 강제 새로고침 유도 (캐시 방지)
  iframe.src = "";
  setTimeout(() => {
    iframe.src = path + "?t=" + Date.now();  // 캐시 무효화
  }, 10);

  // active 클래스 초기화 및 적용
  document.querySelectorAll('nav a').forEach(a => a.classList.remove('active'));
  clicked.classList.add('active');
}
document.addEventListener('DOMContentLoaded', () => {
  const firstNav = document.querySelector('nav a');
  if (firstNav) firstNav.click(); // 초기에 첫 메뉴 클릭 유도
});