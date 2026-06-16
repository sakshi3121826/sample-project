document.addEventListener('DOMContentLoaded', function () {
  setActiveNavigation();
  setupUploadTabs();
});

function setActiveNavigation() {
  const path = window.location.pathname;
  const navLinks = document.querySelectorAll('.main-nav a');
  navLinks.forEach((link) => {
    if (link.getAttribute('href') === path) {
      link.classList.add('active');
    }
  });
}

function setupUploadTabs() {
  const tabButtons = document.querySelectorAll('.tab-button');
  const tabPanels = document.querySelectorAll('.tab-panel');
  if (!tabButtons.length) return;

  tabButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const targetId = button.dataset.tab;
      tabButtons.forEach((item) => item.classList.remove('active'));
      tabPanels.forEach((panel) => panel.classList.remove('active'));
      button.classList.add('active');
      document.getElementById(targetId).classList.add('active');
    });
  });
}
