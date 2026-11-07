/* Behaviour of a problem page: gated hints, the explanation that unlocks after solving or giving up, Tab in the editor. */
(function () {
  "use strict";
  var main = document.getElementById("problem");
  if (!main || !window.DojoProgress) return;
  var id = main.getAttribute("data-problem-id");
  var P = window.DojoProgress;

  // hints: one at a time, and the count is remembered because using hints changes how a solve is graded
  var hints = Array.prototype.slice.call(document.querySelectorAll("#hints .hint"));
  var more = document.getElementById("moreHint");
  var shown = Math.min(P.get(id).hints || 0, hints.length);
  function paintHints() {
    hints.forEach(function (h, i) { h.hidden = i >= shown; });
    if (shown >= hints.length) {
      more.hidden = true;
    } else {
      more.hidden = false;
      more.textContent = "Show hint " + (shown + 1) + " of " + hints.length;
    }
  }
  more.addEventListener("click", function () {
    shown += 1;
    P.update(id, { hints: shown });
    paintHints();
  });
  paintHints();

  // the explanation (idea, complexity, mistakes) stays hidden until the problem is solved or the learner gives up
  var after = document.getElementById("after");
  var giveUp = document.getElementById("giveUp");
  var ask = document.getElementById("giveUpAsk");
  function reveal() {
    after.hidden = false;
    giveUp.hidden = true;
    ask.hidden = true;
  }
  if (P.isRevealed(id)) reveal();
  giveUp.addEventListener("click", function () { giveUp.hidden = true; ask.hidden = false; });
  document.getElementById("giveUpNo").addEventListener("click", function () { ask.hidden = true; giveUp.hidden = false; });
  document.getElementById("giveUpYes").addEventListener("click", function () {
    if (P.get(id).status !== "solved") P.update(id, { status: "gaveup" });
    reveal();
  });

  // walkthrough: step tabs, one explanation at a time, and the lines of the step highlighted in the code
  var tabs = Array.prototype.slice.call(document.querySelectorAll(".wt-tab"));
  var texts = Array.prototype.slice.call(document.querySelectorAll(".wt-text"));
  var codeLines = Array.prototype.slice.call(document.querySelectorAll(".codeview .ln"));
  function pickStep(k) {
    tabs.forEach(function (b, i) { b.setAttribute("aria-pressed", String(i === k)); });
    texts.forEach(function (t, i) { t.hidden = i !== k; });
    var first = +texts[k].getAttribute("data-first"), last = +texts[k].getAttribute("data-last");
    codeLines.forEach(function (ln) {
      var n = +ln.getAttribute("data-n");
      ln.classList.toggle("hl", n >= first && n <= last);
    });
  }
  tabs.forEach(function (b, i) { b.addEventListener("click", function () { pickStep(i); }); });
  if (tabs.length) pickStep(0);

  // editor: Tab inserts four spaces instead of leaving the box
  var editor = document.getElementById("editor");
  editor.addEventListener("keydown", function (e) {
    if (e.key !== "Tab") return;
    e.preventDefault();
    var s = editor.selectionStart;
    editor.value = editor.value.slice(0, s) + "    " + editor.value.slice(editor.selectionEnd);
    editor.selectionStart = editor.selectionEnd = s + 4;
  });
})();
