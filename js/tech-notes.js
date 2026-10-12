(function () {
  "use strict";
  var input = document.getElementById("note-search");
  if (!input) return;
  var cards = Array.from(document.querySelectorAll(".note-card"));
  var months = Array.from(document.querySelectorAll(".note-month"));
  function filter() {
    var words = input.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    var visible = 0;
    cards.forEach(function (card) {
      var haystack = card.dataset.search.toLocaleLowerCase();
      card.hidden = !words.every(function (word) { return haystack.indexOf(word) >= 0; });
      if (!card.hidden) visible += 1;
    });
    months.forEach(function (month) {
      month.hidden = !Array.from(month.querySelectorAll(".note-card")).some(function (card) { return !card.hidden; });
    });
    document.getElementById("note-result").textContent = visible + " 篇文章";
    document.getElementById("note-empty").hidden = visible !== 0;
  }
  input.addEventListener("input", filter);
}());

