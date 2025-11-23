const BASE_URL = "https://app.tawhid.in/go/";
const RECENT_KEY_LIMIT = 6;

const form = document.getElementById("go-form");
const keyInput = document.getElementById("key-input");
const recentSection = document.getElementById("recent-section");
const recentContainer = document.getElementById("recent-keys");

function openGoLink(key) {
  if (!key) return;
  const url = BASE_URL + encodeURIComponent(key.trim());
  chrome.tabs.create({ url });
  saveRecentKey(key.trim());
  window.close();
}

function saveRecentKey(key) {
  chrome.storage.sync.get(["recentKeys"], (data) => {
    let recent = data.recentKeys || [];
    // Remove if already exists
    recent = recent.filter((k) => k !== key);
    // Add to front
    recent.unshift(key);
    // Trim
    recent = recent.slice(0, RECENT_KEY_LIMIT);
    chrome.storage.sync.set({ recentKeys: recent }, renderRecentKeys);
  });
}

function renderRecentKeys() {
  chrome.storage.sync.get(["recentKeys"], (data) => {
    const recent = data.recentKeys || [];
    recentContainer.innerHTML = "";
    if (!recent.length) {
      recentSection.classList.add("hidden");
      return;
    }
    recentSection.classList.remove("hidden");

    recent.forEach((key) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "chip";
      chip.innerHTML = `<span>${key}</span><small>go/${key}</small>`;
      chip.addEventListener("click", () => openGoLink(key));
      recentContainer.appendChild(chip);
    });
  });
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  openGoLink(keyInput.value);
});

document.addEventListener("DOMContentLoaded", () => {
  renderRecentKeys();
  keyInput.focus();
});
