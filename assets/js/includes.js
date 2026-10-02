/*
 * Buildless HTML includes.
 *
 * Any element with data-include="<path>" has that file fetched and dropped in
 * as its contents, so the header and footer live in partials/ instead of being
 * copy-pasted into all three pages.
 *
 * NOTE: fetch() is blocked on file:// URLs, so opening a page by double-clicking
 * it will render without the header and footer. Serve the folder over HTTP
 * instead -- `python3 -m http.server` from the repo root.
 */

(function () {
	"use strict";

	function markCurrentPage(root) {
		var page = document.body.getAttribute("data-page");
		if (!page) return;
		var links = root.querySelectorAll('[data-nav="' + page + '"]');
		Array.prototype.forEach.call(links, function (link) {
			link.classList.add("current-page");
			link.setAttribute("aria-current", "page");
		});
	}

	function wireNav() {
		var overlay = document.getElementById("myNav");
		var openBtn = document.querySelector("[data-nav-open]");
		var closeBtn = document.querySelector("[data-nav-close]");
		if (!overlay) return;

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
	}

	function loadIncludes() {
		var hosts = document.querySelectorAll("[data-include]");
		var pending = Array.prototype.map.call(hosts, function (host) {
			var src = host.getAttribute("data-include");
			return fetch(src)
				.then(function (response) {
					if (!response.ok) throw new Error(src + " -> HTTP " + response.status);
					return response.text();
				})
				.then(function (html) {
					host.innerHTML = html;
					markCurrentPage(host);
				})
				.catch(function (error) {
					console.error("Could not load include " + src + ":", error);
					if (location.protocol === "file:") {
						console.error(
							"Includes need HTTP. Run `python3 -m http.server` in the repo root " +
							"and open http://localhost:8000/ instead of the file directly."
						);
					}
				});
		});
		return Promise.all(pending);
	}

	function start() {
		loadIncludes().then(wireNav);
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", start);
	} else {
		start();
	}
})();
