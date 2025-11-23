const API_BASE = "https://app.tawhid.in/go/api/";

const searchInput = document.getElementById("search-input");
const newLinkBtn = document.getElementById("new-link-btn");
const formSection = document.getElementById("form-section");
const linkForm = document.getElementById("link-form");
const keyField = document.getElementById("key-field");
const urlField = document.getElementById("url-field");
const descField = document.getElementById("desc-field");
const cancelEditBtn = document.getElementById("cancel-edit-btn");
const formStatus = document.getElementById("form-status");

const listLoading = document.getElementById("list-loading");
const listEmpty = document.getElementById("list-empty");
const listError = document.getElementById("list-error");
const linksList = document.getElementById("links-list");
const countBadge = document.getElementById("count-badge");

let allLinks = [];
let currentMode = "create"; // "create" | "edit"
let editingKey = null;

function setFormVisible(visible) {
  if (visible) {
    formSection.classList.remove("hidden");
    keyField.focus();
  } else {
    formSection.classList.add("hidden");
    linkForm.reset();
    formStatus.textContent = "";
    formStatus.classList.remove("error");
    currentMode = "create";
    editingKey = null;
  }
}

function setStatus(message, isError = false) {
  formStatus.textContent = message;
  formStatus.classList.toggle("error", isError);
}

async function fetchLinks(searchTerm = "") {
  listLoading.classList.remove("hidden");
  listEmpty.classList.add("hidden");
  listError.classList.add("hidden");
  linksList.innerHTML = "";
  countBadge.textContent = "…";

  try {
    const url =
      API_BASE + (searchTerm ? `?search=${encodeURIComponent(searchTerm)}` : "");
    const res = await fetch(url, {
      credentials: "include",
      headers: {
        "Accept": "application/json",
      },
    });

    if (!res.ok) {
      throw new Error(`API error ${res.status}`);
    }

    const data = await res.json();
    // Expecting an array of objects like: { key, url, description }
    allLinks = Array.isArray(data) ? data : [];

    renderLinks(allLinks);
  } catch (err) {
    console.error("Failed to load links", err);
    listError.textContent =
      "Failed to load links from app.tawhid.in. Are you logged in and is the API up?";
    listError.classList.remove("hidden");
  } finally {
    listLoading.classList.add("hidden");
  }
}

function renderLinks(links) {
  linksList.innerHTML = "";

  if (!links.length) {
    listEmpty.classList.remove("hidden");
    countBadge.textContent = "0";
    return;
  }

  listEmpty.classList.add("hidden");
  countBadge.textContent = String(links.length);

  links.forEach((link) => {
    const item = document.createElement("div");
    item.className = "link-item";

    const topRow = document.createElement("div");
    topRow.className = "link-top-row";

    const keySpan = document.createElement("div");
    keySpan.className = "link-key";
    const keyText = (link.key || "").trim();
    keySpan.textContent = keyText || "〈no key〉";
    if (keyText) {
      const small = document.createElement("small");
      small.textContent = `go/${keyText}`;
      keySpan.appendChild(small);
    }

    const actions = document.createElement("div");
    actions.className = "link-actions";

    const editBtn = document.createElement("button");
    editBtn.type = "button";
    editBtn.textContent = "Edit";
    editBtn.addEventListener("click", () => startEdit(link));

    const deleteBtn = document.createElement("button");
    deleteBtn.type = "button";
    deleteBtn.textContent = "Delete";
    deleteBtn.classList.add("danger");
    deleteBtn.addEventListener("click", () => deleteLink(link));

    actions.appendChild(editBtn);
    actions.appendChild(deleteBtn);

    topRow.appendChild(keySpan);
    topRow.appendChild(actions);

    const urlDiv = document.createElement("div");
    urlDiv.className = "link-url";
    urlDiv.textContent = link.url || link.target || "";

    const descDiv = document.createElement("div");
    descDiv.className = "link-desc";
    descDiv.textContent = link.description || link.desc || "";

    item.appendChild(topRow);
    item.appendChild(urlDiv);
    if (descDiv.textContent.trim()) {
      item.appendChild(descDiv);
    }

    linksList.appendChild(item);
  });
}

function startEdit(link) {
  currentMode = "edit";
  editingKey = link.key;
  keyField.value = link.key || "";
  urlField.value = link.url || link.target || "";
  descField.value = link.description || link.desc || "";
  setFormVisible(true);
  setStatus("Editing existing link");
}

async function createOrUpdateLink(evt) {
  evt.preventDefault();
  const key = keyField.value.trim();
  const url = urlField.value.trim();
  const description = descField.value.trim();

  if (!key || !url) {
    setStatus("Key and URL are required", true);
    return;
  }

  try {
    setStatus(currentMode === "edit" ? "Updating…" : "Creating…");
    const payload = {
      key,
      url,
      description,
    };

    let endpoint = API_BASE;
    let method = "POST";

    if (currentMode === "edit" && editingKey) {
      endpoint = API_BASE + encodeURIComponent(editingKey) + "/";
      method = "PUT";
    }

    const res = await fetch(endpoint, {
      method,
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(`API error ${res.status}`);
    }

    setStatus(currentMode === "edit" ? "Updated ✔" : "Created ✔");
    await fetchLinks(searchInput.value.trim());
    setTimeout(() => {
      setFormVisible(false);
    }, 400);
  } catch (err) {
    console.error("Save failed", err);
    setStatus("Failed to save. Check console & API.", true);
  }
}

async function deleteLink(link) {
  const key = (link.key || "").trim();
  if (!key) return;

  const ok = confirm(`Delete go/${key}?`);
  if (!ok) return;

  try {
    const endpoint = API_BASE + encodeURIComponent(key) + "/";
    const res = await fetch(endpoint, {
      method: "DELETE",
      credentials: "include",
    });
    if (!res.ok && res.status !== 204) {
      throw new Error(`API error ${res.status}`);
    }
    await fetchLinks(searchInput.value.trim());
  } catch (err) {
    console.error("Delete failed", err);
    alert("Failed to delete. Check console & API.");
  }
}

function setupSearch() {
  let searchTimeout = null;
  searchInput.addEventListener("input", () => {
    const term = searchInput.value.trim();
    if (searchTimeout) clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      fetchLinks(term);
    }, 250);
  });
}

newLinkBtn.addEventListener("click", () => {
  currentMode = "create";
  editingKey = null;
  linkForm.reset();
  setStatus("");
  setFormVisible(true);
});

cancelEditBtn.addEventListener("click", () => {
  setFormVisible(false);
});

linkForm.addEventListener("submit", createOrUpdateLink);

document.addEventListener("DOMContentLoaded", () => {
  setupSearch();
  fetchLinks("");
});
