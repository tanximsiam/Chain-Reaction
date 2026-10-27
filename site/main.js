// Playable mini board: the same rules as board.py, Red vs Blue on one device.
(() => {
  const ROWS = 5, COLS = 6, COLORS = ["var(--p0)", "var(--p1)"], NAMES = ["Red", "Blue"];
  const FLIGHT_MS = 200, MAX_WAVES = 40;
  const section = document.getElementById("try");
  const boardEl = document.getElementById("board");
  const statusEl = document.getElementById("try-status");
  const turnWord = document.getElementById("turn-word");
  if (!boardEl) return;

  let count, owner, turn, moved, busy, winner;
  const cells = [];

  const neighbors = (r, c) => [[r - 1, c], [r + 1, c], [r, c - 1], [r, c + 1]]
    .filter(([y, x]) => y >= 0 && y < ROWS && x >= 0 && x < COLS);
  const capacity = (r, c) => neighbors(r, c).length;
  const unstable = () => {
    const out = [];
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) if (count[r][c] >= capacity(r, c)) out.push([r, c]);
    return out;
  };
  const totals = () => {
    const t = [0, 0];
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) if (owner[r][c] !== null) t[owner[r][c]] += count[r][c];
    return t;
  };
  const checkWinner = () => {
    if (moved.size < 2) return null;
    const t = totals();
    return t[0] === 0 ? 1 : t[1] === 0 ? 0 : null;
  };

  // Atom positions inside a cell, in %, matching the game: 1 centred, 2+ on a small circle.
  const offsets = (n) => n === 1 ? [[50, 50]] : Array.from({ length: n }, (_, i) => {
    const a = Math.PI / 2 + (i * 2 * Math.PI) / n;
    return [50 + 17 * Math.cos(a), 50 - 17 * Math.sin(a)];
  });

  function renderCell(r, c) {
    const el = cells[r * COLS + c];
    const n = count[r][c];
    const wrap = document.createElement("span");
    wrap.className = "atoms-in" + (n && n === capacity(r, c) - 1 ? " spin" : "");
    offsets(n || 0).slice(0, n).forEach(([x, y]) => {
      const a = document.createElement("span");
      a.className = "atom";
      a.style.left = x + "%";
      a.style.top = y + "%";
      a.style.background = COLORS[owner[r][c]];
      wrap.append(a);
    });
    el.replaceChildren(wrap);
    const word = n ? `${n} ${NAMES[owner[r][c]]} atom${n > 1 ? "s" : ""}` : "empty";
    el.setAttribute("aria-label", `Row ${r + 1}, column ${c + 1}: ${word}`);
  }
  const renderAll = () => { for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) renderCell(r, c); };

  function setTurn(p) {
    turn = p;
    section.dataset.turn = p;
    turnWord.textContent = NAMES[p];
  }

  function center(r, c) {
    const box = boardEl.getBoundingClientRect(), cell = cells[r * COLS + c].getBoundingClientRect();
    return [cell.left - box.left + cell.width / 2, cell.top - box.top + cell.height / 2, cell.width];
  }

  const wait = (ms) => new Promise((done) => setTimeout(done, ms));

  async function wave() {
    const flights = [];
    for (const [r, c] of unstable()) {
      const p = owner[r][c];
      count[r][c] -= capacity(r, c);
      if (count[r][c] === 0) owner[r][c] = null;
      for (const n of neighbors(r, c)) flights.push([[r, c], n, p]);
    }
    renderAll();
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const dots = flights.map(([[r, c], , p]) => {
      const [x, y, size] = center(r, c);
      const d = document.createElement("span");
      d.className = "fly";
      Object.assign(d.style, { left: x + "px", top: y + "px", width: size * 0.3 + "px", height: size * 0.3 + "px", background: COLORS[p] });
      boardEl.append(d);
      return d;
    });
    if (!reduce) {
      boardEl.offsetWidth; // commit start positions so the move animates
      flights.forEach(([, [r, c]], i) => {
        const [x, y] = center(r, c);
        dots[i].style.left = x + "px";
        dots[i].style.top = y + "px";
      });
      await wait(FLIGHT_MS);
    }
    dots.forEach((d) => d.remove());
    for (const [, [r, c], p] of flights) { count[r][c] += 1; owner[r][c] = p; }
    renderAll();
  }

  async function play(r, c) {
    if (busy || winner !== null) return;
    if (owner[r][c] !== null && owner[r][c] !== turn) {
      const el = cells[r * COLS + c];
      el.classList.remove("shake"); el.offsetWidth; el.classList.add("shake");
      statusEl.textContent = `That cell is ${NAMES[owner[r][c]]}’s. Pick an empty one or your own.`;
      return;
    }
    busy = true;
    count[r][c] += 1; owner[r][c] = turn; moved.add(turn);
    renderCell(r, c);
    let waves = 0;
    while (unstable().length && checkWinner() === null && waves < MAX_WAVES) { await wave(); waves++; }
    winner = checkWinner();
    busy = false;
    if (winner !== null) {
      statusEl.textContent = `${NAMES[winner]} wins. Every other atom has been captured.`;
      setTurn(winner);
    } else {
      statusEl.textContent = waves > 1 ? `A chain of ${waves} bursts.` : waves === 1 ? "It burst." : "Corners burst at two atoms.";
      setTurn(1 - turn);
    }
  }

  function reset() {
    count = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
    owner = Array.from({ length: ROWS }, () => Array(COLS).fill(null));
    moved = new Set(); busy = false; winner = null;
    setTurn(0);
    statusEl.textContent = "Corners burst at two atoms.";
    renderAll();
  }

  for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "cell";
    b.addEventListener("click", () => play(r, c));
    cells.push(b);
    boardEl.append(b);
  }
  document.getElementById("try-reset").addEventListener("click", reset);
  reset();
})();

// Section entrances: each part rises once as it scrolls in, staggered in document order.
(() => {
  const items = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) { items.forEach((el) => el.classList.add("in")); return; }
  const seen = new IntersectionObserver((entries) => {
    entries.filter((e) => e.isIntersecting).forEach((e, i) => {
      e.target.style.transitionDelay = i * 80 + "ms";
      e.target.classList.add("in");
      seen.unobserve(e.target);
    });
  }, { threshold: 0.15 });
  items.forEach((el) => seen.observe(el));
})();
