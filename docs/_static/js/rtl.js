// RTL JavaScript for reversing navigation arrow icons
function reverseArrows() {
  const prevSvg = document.querySelector(".prev-next-area .left-prev svg");
  const nextSvg = document.querySelector(".prev-next-area .right-next svg");

  if (prevSvg) {
    prevSvg.setAttribute("data-icon", "angle-right");
  }
  if (nextSvg) {
    nextSvg.setAttribute("data-icon", "angle-left");
  }
}

setTimeout(reverseArrows, 100);
