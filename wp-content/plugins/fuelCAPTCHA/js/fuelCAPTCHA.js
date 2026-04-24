/** fuelCAPTCHA v0.0.3 **/

document.addEventListener("DOMContentLoaded", function() {
	let gf = document.querySelectorAll('.gform_wrapper');

	// Setup a new observer to get notified of node changes in Gravity Forms (for ajax changes)
	let fuelCAPTCHAObserver = new MutationObserver(function (mutations) {
		mutations.forEach(function(mutation) {
			// Since the form reloaded with ajax, we need to re-add the event listener
			document.addEventListener('keypress', fuelCAPTCHA_honeypot);
			window.addEventListener('mousemove', fuelCAPTCHA_honeypot);
		});
	});

	if(gf.length > 0) {
		// Run mutation observer
		fuelCAPTCHAObserver.observe(gf[0], {
			childList: true
		});

		// Get Secret
		var xhr = new XMLHttpRequest();
		xhr.open('POST', fuelCAPTCHA_urls.ajax_url);
		xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
		xhr.send('action=fuelCAPTCHA_get_key');

		// Add event listeners
		document.addEventListener('keypress', fuelCAPTCHA_honeypot);
		window.addEventListener('mousemove', fuelCAPTCHA_honeypot);
	}
});

function fuelCAPTCHA_honeypot() {
	document.removeEventListener('keypress', fuelCAPTCHA_honeypot);
	window.removeEventListener('mousemove', fuelCAPTCHA_honeypot);
	var reverseHoneypot = document.querySelectorAll('input[name=name-2]');
	for (var i = 0; i < reverseHoneypot.length; i++) {
		reverseHoneypot[i].setAttribute('value', '');
	}
}