// Elevate Audiology v2 — site behavior
(function () {
  // Mobile nav toggle
  var toggle = document.querySelector('.nav-toggle');
  var navList = document.querySelector('.nav-list');
  if (toggle && navList) {
    toggle.addEventListener('click', function () {
      var open = navList.getAttribute('data-open') === 'true';
      navList.setAttribute('data-open', open ? 'false' : 'true');
      toggle.setAttribute('aria-expanded', open ? 'false' : 'true');
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
