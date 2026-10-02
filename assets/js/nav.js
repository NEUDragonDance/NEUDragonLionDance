/*
 * Overlay navigation menu.
 *
 * The header markup itself is stamped into each page at build time by
 * build.py, so this only handles behaviour: opening and closing the
 * full-screen overlay shown on narrow screens.
 */

document.addEventListener("DOMContentLoaded", function () {
	var overlay = document.getElementById("myNav");
	if (!overlay) return;

	var openBtn = document.querySelector("[data-nav-open]");
	var closeBtn = document.querySelector("[data-nav-close]");

	function setOpen(isOpen) {
		overlay.style.width = isOpen ? "100%" : "0%";
		overlay.setAttribute("aria-hidden", isOpen ? "false" : "true");
		if (openBtn) openBtn.setAttribute("aria-expanded", isOpen ? "true" : "false");
		if (isOpen && closeBtn) closeBtn.focus();
		else if (!isOpen && openBtn) openBtn.focus();
	}

	if (openBtn) openBtn.addEventListener("click", function () { setOpen(true); });
	if (closeBtn) closeBtn.addEventListener("click", function () { setOpen(false); });

	// Dismiss with Escape, and after following a link to an on-page anchor.
	document.addEventListener("keydown", function (event) {
		if (event.key === "Escape" && overlay.offsetWidth > 0) setOpen(false);
	});
	Array.prototype.forEach.call(overlay.querySelectorAll("a"), function (link) {
		link.addEventListener("click", function () { setOpen(false); });
	});
});
