// Elevate Audiology v2 — site behavior
(function () {
  // Mobile nav toggle
  var toggle = document.querySelector('.nav-toggle');
  var navList = document.querySelector('.nav-list');

  // Inject open/close icons (the original markup only has the hamburger).
  // We wrap the existing SVG with class 'icon-open' and append a matching X (icon-close).
  // CSS in the @media (max-width: 1024px) block swaps which is visible based on aria-expanded.
  if (toggle) {
    var existingSvg = toggle.querySelector('svg');
    if (existingSvg && !existingSvg.classList.contains('icon-open')) {
      existingSvg.classList.add('icon-open');
    }
    if (!toggle.querySelector('.icon-close')) {
      var closeSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      closeSvg.setAttribute('class', 'icon-close');
      closeSvg.setAttribute('width', '22');
      closeSvg.setAttribute('height', '22');
      closeSvg.setAttribute('viewBox', '0 0 24 24');
      closeSvg.setAttribute('fill', 'none');
      closeSvg.setAttribute('stroke', 'currentColor');
      closeSvg.setAttribute('stroke-width', '2');
      closeSvg.setAttribute('stroke-linecap', 'round');
      closeSvg.innerHTML = '<path d="M6 6l12 12M18 6l-6 6-6 6"></path>';
      toggle.appendChild(closeSvg);
    }
  }

  function setMenuOpen(open) {
    if (!toggle || !navList) return;
    navList.setAttribute('data-open', open ? 'true' : 'false');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? 'Close navigation menu' : 'Toggle navigation menu');
    // Lock body scroll while drawer is open so the page behind doesn't move
    document.body.style.overflow = open ? 'hidden' : '';
    // When closing, also collapse any open submenu accordions
    if (!open) {
      document.querySelectorAll('.has-drop[data-open="true"]').forEach(function (li) {
        li.setAttribute('data-open', 'false');
      });
    }
  }

  if (toggle && navList) {
    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = navList.getAttribute('data-open') === 'true';
      setMenuOpen(!open);
    });
  }

  // Mobile dropdown toggling
  document.querySelectorAll('.has-drop > a, .has-drop > button').forEach(function (trigger) {
    trigger.addEventListener('click', function (e) {
      if (window.innerWidth <= 1024) {
        e.preventDefault();
        var parent = trigger.parentElement;
        var open = parent.getAttribute('data-open') === 'true';
        parent.setAttribute('data-open', open ? 'false' : 'true');
      }
    });
  });

  // Close the mobile menu when the user taps a leaf nav link (a link that
  // actually navigates somewhere, not a parent accordion trigger).
  if (navList) {
    navList.querySelectorAll('a').forEach(function (a) {
      // Skip the parent accordion triggers (their <li> is .has-drop and the <a> is a direct child)
      var li = a.closest('li');
      var isAccordionTrigger = li && li.classList.contains('has-drop') && a.parentElement === li;
      if (isAccordionTrigger) return;
      a.addEventListener('click', function () {
        if (window.innerWidth <= 1024) {
          setMenuOpen(false);
        }
      });
    });
  }

  // Close menu on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && navList && navList.getAttribute('data-open') === 'true') {
      setMenuOpen(false);
    }
  });

  // Close menu if the viewport grows past the mobile breakpoint
  window.addEventListener('resize', function () {
    if (window.innerWidth > 1024 && navList && navList.getAttribute('data-open') === 'true') {
      setMenuOpen(false);
    }
  });

  // Team modal
  var backdrop = document.querySelector('.team-modal-backdrop');
  var modalPhoto = document.querySelector('.team-modal .modal-photo');
  var modalName = document.querySelector('.team-modal .modal-name');
  var modalRole = document.querySelector('.team-modal .modal-role');
  var modalQuote = document.querySelector('.team-modal .modal-quote');
  var modalBio = document.querySelector('.team-modal .modal-bio');
  var modalCreds = document.querySelector('.team-modal .modal-creds');

  function openModal(card) {
    if (!backdrop) return;
    var photo = card.dataset.photo;
    var name = card.dataset.name;
    var role = card.dataset.role;
    var creds = card.dataset.creds || '';
    var quote = card.dataset.quote || '';
    var bio = card.dataset.bio || 'Full bio coming soon.';

    if (modalPhoto) {
      if (photo) {
        modalPhoto.innerHTML = '<img src="' + photo + '" alt="' + name + '" loading="lazy">';
      } else {
        var initials = name.split(' ').map(function (s) { return s[0]; }).join('').slice(0, 2);
        modalPhoto.innerHTML = '<div class="team-photo placeholder" style="height:100%">' + initials + '</div>';
      }
    }
    if (modalName) modalName.textContent = name;
    if (modalRole) modalRole.textContent = role;
    if (modalCreds) modalCreds.textContent = creds;
    if (modalQuote) {
      if (quote) {
        modalQuote.textContent = '"' + quote + '"';
        modalQuote.style.display = '';
      } else {
        modalQuote.style.display = 'none';
      }
    }
    if (modalBio) modalBio.innerHTML = bio;
    backdrop.setAttribute('data-open', 'true');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    if (!backdrop) return;
    backdrop.setAttribute('data-open', 'false');
    document.body.style.overflow = '';
  }

  document.querySelectorAll('.team-card').forEach(function (card) {
    card.addEventListener('click', function () { openModal(card); });
    card.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openModal(card); }
    });
  });

  if (backdrop) {
    backdrop.addEventListener('click', function (e) {
      if (e.target === backdrop || e.target.classList.contains('close')) closeModal();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeModal();
    });
  }
})();
