document.addEventListener("DOMContentLoaded", function () {
  // Mobile menu toggle
  var btn = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // Photo lightbox. A link with data-lightbox opens its image full size; if it also has
  // data-gallery (a JSON list of image URLs), the viewer can step through them.
  var links = document.querySelectorAll("a[data-lightbox]");
  if (!links.length) return;
  var box = document.createElement("div");
  box.className = "lightbox";
  box.setAttribute("role", "dialog");
  box.setAttribute("aria-modal", "true");
  box.innerHTML =
    '<button type="button" class="lb-close" aria-label="Close">&times;</button>' +
    '<button type="button" class="lb-prev" aria-label="Previous photo">&#8249;</button>' +
    '<img alt=""><video controls playsinline hidden></video>' +
    '<button type="button" class="lb-next" aria-label="Next photo">&#8250;</button>' +
    '<div class="lb-count" aria-live="polite"></div>';
  document.body.appendChild(box);
  var big = box.querySelector("img"), vid = box.querySelector("video"), count = box.querySelector(".lb-count");
  var prev = box.querySelector(".lb-prev"), next = box.querySelector(".lb-next");
  var list = [], idx = 0;

  function show(i) {
    idx = (i + list.length) % list.length;
    var isVid = /\.mp4(\?|$)/i.test(list[idx]);
    vid.pause();
    if (isVid) { big.hidden = true; big.removeAttribute("src"); vid.hidden = false; vid.src = list[idx]; vid.play().catch(function () {}); }
    else { vid.hidden = true; vid.removeAttribute("src"); big.hidden = false; big.src = list[idx]; }
    var multi = list.length > 1;
    prev.hidden = next.hidden = !multi;
    count.textContent = multi ? (idx + 1) + " / " + list.length : "";
    // warm the next image so stepping feels instant
    var nx = list[(idx + 1) % list.length];
    if (multi && !/\.mp4(\?|$)/i.test(nx)) { var pre = new Image(); pre.src = nx; }
  }
  function close() { box.classList.remove("open"); big.removeAttribute("src"); vid.pause(); vid.removeAttribute("src"); list = []; }

  links.forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      var g = a.getAttribute("data-gallery");
      try { list = g ? JSON.parse(g) : [a.href]; } catch (err) { list = [a.href]; }
      var thumb = a.querySelector("img");
      big.alt = thumb ? thumb.alt : "";
      show(0);
      box.classList.add("open");
      box.querySelector(".lb-close").focus();
    });
  });

  prev.addEventListener("click", function (e) { e.stopPropagation(); show(idx - 1); });
  next.addEventListener("click", function (e) { e.stopPropagation(); show(idx + 1); });
  big.addEventListener("click", function (e) { if (list.length > 1) { e.stopPropagation(); show(idx + 1); } });
  vid.addEventListener("click", function (e) { e.stopPropagation(); });
  box.addEventListener("click", close);
  document.addEventListener("keydown", function (e) {
    if (!box.classList.contains("open")) return;
    if (e.key === "Escape") close();
    else if (e.key === "ArrowRight" && list.length > 1) show(idx + 1);
    else if (e.key === "ArrowLeft" && list.length > 1) show(idx - 1);
  });
  // swipe on phones
  var x0 = null;
  box.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  box.addEventListener("touchend", function (e) {
    if (x0 === null || list.length < 2) return;
    var dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 40) show(idx + (dx < 0 ? 1 : -1));
  });
});
