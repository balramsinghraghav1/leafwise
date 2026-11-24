(function () {
  // show times in the visitor's own time zone
  document.querySelectorAll("time[data-local]").forEach(function (t) {
    var d = new Date(t.getAttribute("datetime"));
    if (!isNaN(d)) t.textContent = d.toLocaleString([], { dateStyle: "medium", timeStyle: "short" });
  });
  // confirm before destructive actions
  document.querySelectorAll("form[data-confirm]").forEach(function (f) {
    f.addEventListener("submit", function (e) { if (!window.confirm(f.dataset.confirm)) e.preventDefault(); });
  });
  // history filter
  var chips = document.querySelectorAll(".chip");
  if (chips.length) {
    chips.forEach(function (c) {
      c.addEventListener("click", function () {
        chips.forEach(function (x) { x.classList.toggle("on", x === c); });
        var shown = 0;
        document.querySelectorAll(".scan-card").forEach(function (card) {
          var ok = c.dataset.filter === "all" || card.dataset.kind === c.dataset.filter;
          card.hidden = !ok; if (ok) shown++;
        });
        var n = document.getElementById("none-match"); if (n) n.hidden = shown > 0;
      });
    });
  }
  // guide search
  var q = document.getElementById("q");
  if (q) {
    q.addEventListener("input", function () {
      var term = q.value.trim().toLowerCase(), any = false;
      document.querySelectorAll(".g-crop").forEach(function (sec) {
        var crop = sec.dataset.name, cropHit = !term || crop.indexOf(term) !== -1, n = 0;
        sec.querySelectorAll(".g-item").forEach(function (it) {
          var hit = cropHit || it.dataset.text.indexOf(term) !== -1;
          it.hidden = !hit; if (hit) n++;
        });
        sec.hidden = n === 0; if (n) any = true;
      });
      document.getElementById("no-hit").hidden = any;
    });
    if (location.hash) { var t = document.querySelector(location.hash); if (t) t.querySelector("details") && (t.querySelector("details").open = true); }
  }
})();
