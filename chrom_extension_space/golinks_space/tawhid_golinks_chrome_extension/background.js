const BASE_URL = "https://app.tawhid.in/go/";

chrome.omnibox.onInputChanged.addListener((text, suggest) => {
  const key = text.trim() || "your-key";
  suggest([
    {
      content: text,
      description: `Open go/<match> at app.tawhid.in — <url>${BASE_URL}${key}</url>`,
    },
  ]);
});

chrome.omnibox.onInputEntered.addListener((text, disposition) => {
  const key = text.trim();
  if (!key) return;
  const url = BASE_URL + encodeURIComponent(key);

  switch (disposition) {
    case "currentTab":
      chrome.tabs.update({ url });
      break;
    case "newForegroundTab":
      chrome.tabs.create({ url });
      break;
    case "newBackgroundTab":
      chrome.tabs.create({ url, active: false });
      break;
    default:
      chrome.tabs.create({ url });
  }
});
