// Dependency-free frontend for the lesson viewer.
// Fetches JSON from the FastAPI backend and injects the server-rendered HTML.

const state = {
  tracks: [],
  lessons: [], // all LessonSummary, numeric order
  currentTrack: null,
  query: "", // lesson filter text (matches id or title)
  openLesson: null, // lesson_id currently expanded
  activeItem: null, // `${lesson_id}/${item_id}`
};

async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `${res.status} ${res.statusText}`);
  }
  return res.json();
}

function lessonsForTrack(trackName) {
  const track = state.tracks.find((t) => t.name === trackName);
  const ids = track ? track.lesson_ids : [];
  // Keep track order, but only lessons that actually exist on disk.
  const present = new Map(state.lessons.map((l) => [l.lesson_id, l]));
  return ids.map((id) => present.get(id)).filter(Boolean);
}

function renderTrackPicker() {
  const select = document.getElementById("track-select");
  select.innerHTML = "";
  for (const track of state.tracks) {
    const opt = document.createElement("option");
    opt.value = track.name;
    const count = lessonsForTrack(track.name).length;
    opt.textContent = `${track.name} (${count})`;
    select.appendChild(opt);
  }
  select.value = state.currentTrack;
  select.onchange = () => {
    state.currentTrack = select.value;
    state.openLesson = null;
    renderLessonList();
  };
}

function matchesQuery(lesson) {
  const q = state.query.trim().toLowerCase();
  if (!q) return true;
  return (
    lesson.lesson_id.toLowerCase().includes(q) ||
    lesson.title.toLowerCase().includes(q)
  );
}

function renderLessonList() {
  const nav = document.getElementById("lesson-list");
  nav.innerHTML = "";
  const lessons = lessonsForTrack(state.currentTrack).filter(matchesQuery);
  if (lessons.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty-note";
    empty.textContent = state.query
      ? `No lessons match “${state.query}”.`
      : "No lessons in this track.";
    nav.appendChild(empty);
    return;
  }
  for (const lesson of lessons) {
    nav.appendChild(renderLesson(lesson));
  }
}

// mini ⊆ full, so a lesson in the mini track is the notable case; everything
// else is full-only. Show whichever applies as a coloured pill.
function trackBadge(lesson) {
  const inMini = lesson.tracks.includes("mini");
  const cls = inMini ? "track-badge track-mini" : "track-badge track-full";
  const label = inMini ? "mini" : "full";
  return `<span class="${cls}">${label}</span>`;
}

function renderLesson(lesson) {
  const wrap = document.createElement("div");
  wrap.className = "lesson";

  const toggle = document.createElement("button");
  toggle.className = "lesson-toggle";
  toggle.innerHTML =
    `<span class="lesson-num">${lesson.lesson_id}</span>` +
    `<span class="lesson-title">${escapeHtml(lesson.title)}</span>` +
    trackBadge(lesson) +
    `<span class="lesson-count">${lesson.item_count}</span>`;
  toggle.onclick = () => {
    state.openLesson = state.openLesson === lesson.lesson_id ? null : lesson.lesson_id;
    renderLessonList();
  };
  wrap.appendChild(toggle);

  if (state.openLesson === lesson.lesson_id) {
    const list = document.createElement("ul");
    list.className = "item-list";
    getJSON(`/api/lessons/${lesson.lesson_id}`)
      .then((detail) => {
        for (const item of detail.items) {
          list.appendChild(renderItemLink(lesson.lesson_id, item));
        }
      })
      .catch((err) => {
        const li = document.createElement("li");
        li.textContent = `Failed to load: ${err.message}`;
        list.appendChild(li);
      });
    wrap.appendChild(list);
  }
  return wrap;
}

// Short format tag shown on each item row.
function itemBadgeLabel(fmt) {
  if (fmt === "notebook") return "ipynb";
  if (fmt === "html") return "slides ↗";
  return "md";
}

function renderItemLink(lessonId, item) {
  const li = document.createElement("li");
  // Color-code the row by kind (lecture / lab / intro / …); see .kind-* in style.css.
  li.className = `kind-${item.kind}`;
  const key = `${lessonId}/${item.item_id}`;
  const badge = `<span class="badge">${itemBadgeLabel(item.fmt)}</span>`;

  // Standalone HTML slide decks are full documents, not injectable fragments:
  // link straight to the raw file and open it in its own tab.
  if (item.fmt === "html") {
    const link = document.createElement("a");
    link.href = `/api/lessons/${lessonId}/items/${item.item_id}/raw`;
    link.target = "_blank";
    link.rel = "noopener";
    link.innerHTML = escapeHtml(item.title) + badge;
    li.appendChild(link);
    return li;
  }

  const btn = document.createElement("button");
  btn.innerHTML = escapeHtml(item.title) + badge;
  if (state.activeItem === key) btn.classList.add("active");
  btn.onclick = () => openItem(lessonId, item);
  li.appendChild(btn);
  return li;
}

async function openItem(lessonId, item) {
  state.activeItem = `${lessonId}/${item.item_id}`;
  renderLessonList();
  document.getElementById("welcome").hidden = true;
  const view = document.getElementById("item-view");
  view.hidden = false;
  const meta = document.getElementById("item-meta");
  const body = document.getElementById("item-html");
  meta.textContent = `${lessonId} · ${item.filename}`;
  body.innerHTML = "Loading…";
  try {
    const rendered = await getJSON(
      `/api/lessons/${lessonId}/items/${item.item_id}`
    );
    body.innerHTML = rendered.html;
  } catch (err) {
    body.innerHTML = `<div class="error-banner">Failed to render: ${escapeHtml(
      err.message
    )}</div>`;
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

async function init() {
  try {
    const [tracks, lessons] = await Promise.all([
      getJSON("/api/tracks"),
      getJSON("/api/lessons"),
    ]);
    state.tracks = tracks;
    state.lessons = lessons;
    // Default to the "mini" track when it exists; otherwise the first track.
    const mini = tracks.find((t) => t.name === "mini");
    state.currentTrack = mini ? mini.name : tracks.length ? tracks[0].name : null;
    const search = document.getElementById("lesson-search");
    search.oninput = () => {
      state.query = search.value;
      renderLessonList();
    };
    renderTrackPicker();
    renderLessonList();
  } catch (err) {
    document.getElementById("lesson-list").innerHTML =
      `<div class="error-banner">Could not load catalog: ${escapeHtml(
        err.message
      )}</div>`;
  }
}

init();
