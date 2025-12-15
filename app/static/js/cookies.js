(function() {
    // Check if cookies have been accepted
    if (!localStorage.getItem('cookiesAccepted')) {
        // Create the cookie consent popup
        var cookiePopup = document.createElement('div');
        cookiePopup.id = 'cookiePopup';
        cookiePopup.style.position = 'fixed';
        cookiePopup.style.bottom = '0';
        cookiePopup.style.left = '0';
        cookiePopup.style.right = '0';
        cookiePopup.style.backgroundColor = '#333';
        cookiePopup.style.color = 'white';
        cookiePopup.style.padding = '15px';
        cookiePopup.style.textAlign = 'center';
        cookiePopup.style.zIndex = '9999';
        
        // Content for the popup
        cookiePopup.innerHTML = `
            <p>We use cookies to enhance your experience. By continuing to visit this site, you agree to our use of cookies. <a href="#" style="color: #4CAF50;">Learn more</a></p>
            <button id="acceptCookies" style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; margin: 5px; cursor: pointer;">Accept</button>
            <button id="declineCookies" style="background-color: #f44336; color: white; padding: 10px 20px; border: none; margin: 5px; cursor: pointer;">Decline</button>
        `;

        // Append the popup to the body
        document.body.appendChild(cookiePopup);

        // Accept Cookies
        document.getElementById('acceptCookies').addEventListener('click', function() {
            localStorage.setItem('cookiesAccepted', 'true');
            cookiePopup.style.display = 'none';
        });

        // Decline Cookies
        document.getElementById('declineCookies').addEventListener('click', function() {
            cookiePopup.style.display = 'none';
        });
    }
})();