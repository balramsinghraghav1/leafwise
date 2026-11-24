(function () {
  var $ = function (s) { return document.querySelector(s); };
  var el = function (tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; };
  var pct = function (x) { return (x * 100).toFixed(1) + "%"; };
  var csrf = document.querySelector('meta[name="csrf-token"]').content;
  var chosen = null, url = null;

  function showError(msg) { var p = $("#form-error"); p.textContent = msg || ""; p.hidden = !msg; }
  function refresh() { $("#go").disabled = !(chosen && window.MODEL_READY); $("#reset").hidden = !chosen; }

  function setFile(f) {
    if (!f) return;
    if (!/^image\//.test(f.type)) return showError("Please choose an image file.");
    if (f.size > 8 * 1024 * 1024) return showError("That image is larger than 8 MB. Please use a smaller photo.");
    showError("");
    chosen = f;
    if (url) URL.revokeObjectURL(url);
    url = URL.createObjectURL(f);
    var img = $("#preview"); img.src = url; img.hidden = false; $("#drop-text").hidden = true;
    refresh();
  }
  function clearAll() {
    chosen = null; if (url) URL.revokeObjectURL(url); url = null;
    $("#preview").hidden = true; $("#preview").removeAttribute("src"); $("#drop-text").hidden = false;
    $("#file").value = ""; $("#camera").value = ""; showError(""); refresh();
  }

  $("#file").addEventListener("change", function (e) { setFile(e.target.files[0]); });
  $("#camera").addEventListener("change", function (e) { setFile(e.target.files[0]); });
  $("#camera-btn").addEventListener("click", function () { $("#camera").click(); });
  $("#reset").addEventListener("click", clearAll);
  var drop = $("#drop");
  drop.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); $("#file").click(); } });
  ["dragenter", "dragover"].forEach(function (n) { drop.addEventListener(n, function (e) { e.preventDefault(); drop.classList.add("over"); }); });
  ["dragleave", "drop"].forEach(function (n) { drop.addEventListener(n, function (e) { e.preventDefault(); drop.classList.remove("over"); }); });
  drop.addEventListener("drop", function (e) { setFile(e.dataTransfer.files[0]); });

  function render(data) {
    var res = data.result, top = res.top[0], adv = data.advice;
    $("#empty").hidden = true; $("#out").hidden = false;
    var tag = $("#tag"); tag.textContent = top.healthy ? "Healthy" : "Problem found"; tag.className = "tag " + (top.healthy ? "ok" : "bad");
    var cause = $("#cause"); cause.textContent = adv ? adv.cause_label : ""; cause.hidden = !adv;
    $("#disease").textContent = top.healthy ? top.crop + " leaf looks healthy" : top.disease;
    $("#crop-line").textContent = top.crop + " · " + pct(top.confidence) + " confident";
    $("#low").hidden = top.confidence >= 0.6;
    $("#about").textContent = adv ? adv.about : "";
    var ul = $("#actions"); ul.replaceChildren();
    ((adv && adv.actions) || []).forEach(function (a) { ul.append(el("li", "", a)); });
    var bars = $("#bars"); bars.replaceChildren();
    res.top.forEach(function (t) {
      var li = el("li"), row = el("div", "row");
      row.append(el("span", "", t.crop + " · " + t.disease), el("span", "", pct(t.confidence)));
      var track = el("div", "track"), fill = el("div", "fill"); fill.style.width = (t.confidence * 100).toFixed(1) + "%";
      track.append(fill); li.append(row, track); bars.append(li);
    });
    $("#meta").textContent = "Analysed in " + res.ms + " ms";
    var note = $("#note"); note.textContent = data.note || ""; note.hidden = !data.note;
    var rep = $("#report"); if (data.scan_url) { rep.href = data.scan_url; rep.hidden = false; } else { rep.hidden = true; }
  }

  $("#form").addEventListener("submit", async function (e) {
    e.preventDefault();
    if (!chosen) return;
    var btn = $("#go"); btn.disabled = true; btn.textContent = "Analysing…"; showError("");
    var fd = new FormData(); fd.append("image", chosen); fd.append("crop", $("#crop").value);
    try {
      var r = await fetch("/api/predict", { method: "POST", body: fd, headers: { "X-CSRF-Token": csrf } });
      if (r.status === 401) { window.location.href = "/login?next=/detect"; return; }
      var data = {}; try { data = await r.json(); } catch (_) {}
      if (!r.ok) throw new Error(data.error || "Something went wrong. Please try again.");
      render(data);
    } catch (err) { showError(err.message); }
    finally { btn.textContent = "Analyse leaf"; refresh(); }
  });
  refresh();
})();
