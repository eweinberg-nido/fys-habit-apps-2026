// Angelfire-style hit counter. Decorative only: the number is fixed.
// Usage: <div class="hitcounter" data-value="2026"></div> then load this script.
(function () {
  var SEGMENTS = {
    a: "8,3 32,3 35,6 32,9 8,9 5,6",
    b: "35,8 38,11 38,30 35,33 32,30 32,11",
    c: "35,37 38,40 38,59 35,62 32,59 32,40",
    d: "8,61 32,61 35,64 32,67 8,67 5,64",
    e: "5,37 8,40 8,59 5,62 2,59 2,40",
    f: "5,8 8,11 8,30 5,33 2,30 2,11",
    g: "8,32 32,32 35,35 32,38 8,38 5,35"
  };
  var DIGITS = ["abcdef", "bc", "abdeg", "abcdg", "bcfg", "acdfg", "acdefg", "abc", "abcdefg", "abcdfg"];
  var SVG = "http://www.w3.org/2000/svg";

  var css =
    ".hitcounter{display:inline-block;padding:4px;background:linear-gradient(#a9c1ea,#5f80bb);" +
    "border:2px outset #c9d8f3;box-shadow:2px 2px 0 rgba(0,0,0,.35);line-height:0}" +
    ".hitcounter .lcd{display:inline-flex;gap:3px;padding:5px 7px;background:#020802;border:2px inset #2f3d24}" +
    ".hitcounter svg{width:22px;height:33px}" +
    ".hitcounter .off{fill:rgba(80,255,60,.07)}" +
    ".hitcounter .on{fill:#7dff4f;filter:drop-shadow(0 0 2px rgba(110,255,70,.85))}";
  var style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  function digitSvg() {
    var svg = document.createElementNS(SVG, "svg");
    svg.setAttribute("viewBox", "0 0 47 70");
    svg.setAttribute("aria-hidden", "true");
    var g = document.createElementNS(SVG, "g");
    g.setAttribute("transform", "translate(7 0) skewX(-6)");
    for (var k in SEGMENTS) {
      var p = document.createElementNS(SVG, "polygon");
      p.setAttribute("points", SEGMENTS[k]);
      p.setAttribute("data-seg", k);
      g.appendChild(p);
    }
    svg.appendChild(g);
    return svg;
  }

  function setDigit(svg, d) {
    var lit = DIGITS[d];
    var polys = svg.querySelectorAll("polygon");
    for (var i = 0; i < polys.length; i++) {
      polys[i].setAttribute("class", lit.indexOf(polys[i].getAttribute("data-seg")) >= 0 ? "on" : "off");
    }
  }

  Array.prototype.forEach.call(document.querySelectorAll(".hitcounter"), function (box) {
    var target = parseInt(box.getAttribute("data-value"), 10) || 0;
    var width = parseInt(box.getAttribute("data-digits"), 10) || 6;
    box.setAttribute("role", "img");
    box.setAttribute("aria-label", "Visitor counter: " + target);

    var lcd = document.createElement("span");
    lcd.className = "lcd";
    var cells = [];
    for (var i = 0; i < width; i++) { cells.push(digitSvg()); lcd.appendChild(cells[i]); }
    box.appendChild(lcd);

    function show(n) {
      var s = String(n);
      while (s.length < width) s = "0" + s;
      for (var i = 0; i < width; i++) setDigit(cells[i], +s.charAt(i));
    }

    // Roll up to the number on load, like the page just "counted" you
    if (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches) { show(target); return; }
    var start = null;
    function step(t) {
      if (!start) start = t;
      var p = Math.min((t - start) / 1400, 1);
      show(Math.round(target * (1 - Math.pow(1 - p, 3))));
      if (p < 1) requestAnimationFrame(step);
    }
    show(0);
    requestAnimationFrame(step);
  });
})();
