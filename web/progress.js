/* Per-learner progress, kept in this browser's localStorage. P0.6 builds the review queue on top of it.
   Shape: { "<problem id>": { status: "new" | "attempted" | "solved" | "gaveup", hints: <number> } } */
(function (global) {
  "use strict";
  var KEY = "dojo:progress:v1";
  var memory = {};  // used when localStorage is blocked, so the page still works for the session

  function read() {
    try {
      var raw = global.localStorage.getItem(KEY);
      return raw ? JSON.parse(raw) || {} : memory;
    } catch (e) {
      return memory;
    }
  }

  function write(all) {
    memory = all;
    try { global.localStorage.setItem(KEY, JSON.stringify(all)); } catch (e) { /* keep the in-memory copy */ }
  }

  var Progress = {
    get: function (id) {
      var cur = read()[id];
      return cur || { status: "new", hints: 0 };
    },
    update: function (id, patch) {
      var all = read();
      var cur = all[id] || { status: "new", hints: 0 };
      Object.keys(patch).forEach(function (k) { cur[k] = patch[k]; });
      all[id] = cur;
      write(all);
      return cur;
    },
    isRevealed: function (id) {
      var s = Progress.get(id).status;
      return s === "solved" || s === "gaveup";
    }
  };
  global.DojoProgress = Progress;
})(window);
