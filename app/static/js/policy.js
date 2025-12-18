// policy-popup.js
(function () {

  const policies = {
    privacy: `
      <h2>Privacy Policy</h2>
      <p><strong>Last updated:</strong> 2025</p>

      <p>
        Rolsa Technologies (“we”, “our”, “us”) is committed to protecting your privacy.
        This Privacy Policy explains how we collect, use, and protect your personal
        information when you use our website.
      </p>

      <h3>1. Information We Collect</h3>
      <ul>
        <li>Name, email address, and username when you register or log in</li>
        <li>Booking details such as appointment date, time, and notes</li>
        <li>Basic usage data to improve site performance</li>
      </ul>
      <p>We do not collect payment or card details.</p>

      <h3>2. How We Use Your Information</h3>
      <ul>
        <li>To manage user accounts</li>
        <li>To process consultation bookings</li>
        <li>To communicate regarding bookings or account issues</li>
        <li>To improve our website and services</li>
      </ul>

      <h3>3. Data Storage and Security</h3>
      <p>
        Your data is stored securely. Passwords are hashed and never stored in plain text.
        Access to admin features is restricted to authorised users only.
      </p>

      <h3>4. Sharing Your Data</h3>
      <p>
        We do not sell, rent, or trade your personal information.
        Data is only shared if legally required or necessary to protect site security.
      </p>

      <h3>5. Cookies</h3>
      <p>
        Cookies are used to maintain login sessions and improve user experience.
        You may disable cookies in your browser, though some features may not function correctly.
      </p>

      <h3>6. Your Rights</h3>
      <ul>
        <li>Request access to your personal data</li>
        <li>Request corrections</li>
        <li>Request deletion of your account</li>
      </ul>

      <h3>7. Third-Party Links</h3>
      <p>
        Our website may contain links to external sites.
        We are not responsible for their privacy practices.
      </p>

      <h3>8. Policy Updates</h3>
      <p>
        This policy may be updated from time to time.
        Changes will be reflected here.
      </p>

      <h3>9. Contact</h3>
      <p>
        <strong>Email:</strong> support@rolsatechnologies.com<br>
        <strong>Company:</strong> Rolsa Technologies
      </p>
    `,

    cookies: `
      <h2>Cookie Policy</h2>
      <p><strong>Last updated:</strong> 2025</p>

      <p>
        This website uses cookies to ensure proper functionality and improve user experience.
      </p>

      <h3>What Are Cookies?</h3>
      <p>
        Cookies are small text files stored on your device when you visit a website.
      </p>

      <h3>How We Use Cookies</h3>
      <ul>
        <li>Session management (login/logout)</li>
        <li>Security and authentication</li>
        <li>Basic site analytics</li>
      </ul>

      <h3>Managing Cookies</h3>
      <p>
        You can control or delete cookies through your browser settings.
        Disabling cookies may affect site functionality.
      </p>
    `
  };

  /* --- Everything below remains unchanged --- */

  const overlay = document.createElement("div");
  overlay.style = `
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.5);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 9999;
  `;

  const modal = document.createElement("div");
  modal.style = `
    background: #fff;
    width: 90%;
    max-width: 640px;
    height: 500px; /* fixed height */
    border-radius: 12px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.25);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  `;

  const tabs = document.createElement("div");
  tabs.style = `
    display: flex;
    background: #f1f1f1;
    border-bottom: 1px solid #ddd;
  `;
  tabs.innerHTML = `
    <button class="tab-btn active" data-policy="privacy"
      style="flex:1; padding:.75rem; border:0; background:#fff; cursor:pointer; border-right:1px solid #ddd;">
      Privacy
    </button>
    <button class="tab-btn" data-policy="cookies"
      style="flex:1; padding:.75rem; border:0; background:#f1f1f1; cursor:pointer;">
      Cookies
    </button>
    <button id="popupClose" style="
      padding:.75rem 1rem;
      border:0;
      background:none;
      cursor:pointer;
      font-size:1.4rem;
      color:#666;
    ">&times;</button>
  `;

  const body = document.createElement("div");
  body.style = `
    padding: 1rem 1.25rem;
    overflow-y: auto;  /* scrollable content */
    flex: 1;            /* fill remaining modal height */
    line-height: 1.6;
  `;
  body.innerHTML = policies.privacy;

  modal.appendChild(tabs);
  modal.appendChild(body);
  overlay.appendChild(modal);
  document.body.appendChild(overlay);

  function openPopup() {
    overlay.style.display = "flex";
    document.body.style.overflow = "hidden";
  }

  function closePopup() {
    overlay.style.display = "none";
    document.body.style.overflow = "";
  }

  document.addEventListener("click", e => {
    if (e.target.id === "policy-link") {
      e.preventDefault();
      openPopup();
    }
  });

  document.getElementById("popupClose").onclick = closePopup;

  overlay.addEventListener("click", e => {
    if (e.target === overlay) closePopup();
  });

  document.addEventListener("click", e => {
    const btn = e.target.closest(".tab-btn");
    if (!btn) return;

    const type = btn.dataset.policy;
    body.innerHTML = policies[type]; // update content

    document.querySelectorAll(".tab-btn").forEach(b => {
      b.classList.remove("active");
      b.style.background = "#f1f1f1";
    });

    btn.classList.add("active");
    btn.style.background = "#fff";
  });

})();