// Dependency-free frontend for the lesson viewer.
// Fetches JSON from the FastAPI backend and injects the server-rendered HTML.

const state = {
  tracks: [],
  lessons: [], // all LessonSummary, numeric order
  currentTrack: null,
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

function renderLessonList() {
  const nav = document.getElementById("lesson-list");
  nav.innerHTML = "";
  for (const lesson of lessonsForTrack(state.currentTrack)) {
    nav.appendChild(renderLesson(lesson));
  }
}

function renderLesson(lesson) {
  const wrap = document.createElement("div");
  wrap.className = "lesson";

  const toggle = document.createElement("button");
  toggle.className = "lesson-toggle";
  toggle.innerHTML =
    `<span class="lesson-num">${lesson.lesson_id}</span>` +
    `<span class="lesson-title">${escapeHtml(lesson.title)}</span>` +
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

function renderItemLink(lessonId, item) {
  const li = document.createElement("li");
  const btn = document.createElement("button");
  const key = `${lessonId}/${item.item_id}`;
  btn.innerHTML =
    escapeHtml(item.title) +
    `<span class="badge">${item.fmt === "notebook" ? "ipynb" : "md"}</span>`;
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
    state.currentTrack = tracks.length ? tracks[0].name : null;
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
