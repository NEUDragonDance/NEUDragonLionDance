/*
 * Scroll-triggered fade-in animations.
 *
 * Elements tagged .fade-in / .fade-in-2 start transparent and get .visible the
 * first time they scroll into view. Navigation behaviour lives in includes.js.
 */

document.addEventListener("DOMContentLoaded", function () {
	var targets = document.querySelectorAll(".fade-in, .fade-in-2");

	// Without IntersectionObserver, show everything rather than leaving the
	// page blank -- .fade-in sets opacity: 0 until .visible is added.
	if (!("IntersectionObserver" in window)) {
		Array.prototype.forEach.call(targets, function (target) {
			target.classList.add("visible");
		});
		return;
	}

	var observer = new IntersectionObserver(function (entries) {
		entries.forEach(function (entry) {
			if (!entry.isIntersecting) return;
			entry.target.classList.add("visible");
			observer.unobserve(entry.target); // Only animate once.
		});
	}, { root: null, rootMargin: "0px", threshold: 0.1 });

	Array.prototype.forEach.call(targets, function (target) {
		observer.observe(target);
	});
});
