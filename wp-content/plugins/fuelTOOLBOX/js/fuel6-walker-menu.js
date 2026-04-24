/**
 * Add .js-active to <body> if JavaScript is running.
 * Fallback: without it, CSS handles sub-menu behavior.
 * Version: 1.4.0
 */
document.addEventListener('DOMContentLoaded', () => {
	document.body.classList.add('js-active');
	const fuel6_walker_menu = document.querySelectorAll('.fuel6-walker-menu');
	
	for (let i = 0; i < fuel6_walker_menu.length; i++) {
		const menu = fuel6_walker_menu[i];
		//const menu = document.querySelector('.fuel6-walker-menu');
		const openers = menu.querySelectorAll('.menu-link[aria-haspopup]');
		const backLinks = menu.querySelectorAll('.back-link');

		function closeAllSubmenus() {
			openers.forEach(opener => opener.setAttribute('aria-expanded', 'false'));
			menu.querySelectorAll('.active').forEach(sub => sub.classList.remove('active'));
		}

		openers.forEach(opener => {
			opener.addEventListener('click', (e) => {
				e.preventDefault();

				const parentUl = opener.closest('ul');
				const targetId = opener.getAttribute('aria-controls');
				const targetEl = targetId ? document.getElementById(targetId) : null;
				const isExpanded = opener.getAttribute('aria-expanded') === 'true';

				if (isExpanded) {
					// Just close this one
					opener.setAttribute('aria-expanded', 'false');
					targetEl?.classList.remove('active');
				} else {
					// Close all siblings first
					parentUl.querySelectorAll('.menu-link[aria-haspopup]').forEach(siblingBtn => {
						const siblingTargetId = siblingBtn.getAttribute('aria-controls') || siblingBtn.getAttribute('href')?.replace(/^#/, '');
						const siblingTargetEl = siblingTargetId ? document.getElementById(siblingTargetId) : null;

						siblingBtn.setAttribute('aria-expanded', 'false');
						siblingTargetEl?.classList.remove('active');
					});

					// Then open this one
					opener.setAttribute('aria-expanded', 'true');
					targetEl?.classList.add('active');
				}
			});
		});

		backLinks.forEach(backLink => {
			backLink.addEventListener('click', (e) => {
				e.preventDefault();

				const subMenu = backLink.closest('.sub-menu.active');
				const submenuId = subMenu.getAttribute('id');
				const opener = menu.querySelector(`.menu-link[aria-controls="${submenuId}"]`);

				subMenu.classList.remove('active'); // Close the submenu
				opener.setAttribute('aria-expanded', 'false'); // reset the opener's aria-expanded
				opener.focus(); // Focus on the opener link again
			});
		});

		// Close menus on Escape
		document.addEventListener('keydown', (e) => {
			if (e.key === 'Escape') {
				closeAllSubmenus();
			}
		});

		// Close menus when clicking outside
		document.addEventListener('click', (e) => {
			if (!menu.contains(e.target)) {
				closeAllSubmenus();
			}
		});
	}; // End of forEach fuel6_walker_menu loop
});