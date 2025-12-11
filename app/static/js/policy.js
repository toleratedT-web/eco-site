// policy-popup.js
(function () {

  // Your policies
  const policies = {
    privacy: `
      <h2>Privacy Policy</h2>
      <p><strong>Last updated:</strong> Today</p>
      <p>This is where your privacy policy text goes.</p>
      <p>Add as much text as you want — it scrolls.</p>
    `,
    cookies: `
      <h2>Cookie Policy</h2>
      <p><strong>Last updated:</strong> Today</p>
      <p>This is your cookie policy content.</p>
      <p>Replace this with your own info.</p>
    `
  };

  // Overlay
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

  // Modal
  const modal = document.createElement("div");
  modal.style = `
    background: #fff;
    width: 90%;
    max-width: 640px;
    max-height: 80vh;
    border-radius: 12px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.25);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  `;

  // Tabs
  const tabs = document.createElement("div");
  tabs.style = `
    display: flex;
    background: #f1f1f1;
    border-bottom: 1px solid #ddd;
  `;
  tabs.innerHTML = `
    <button class="tab-btn active" data-policy="privacy" 
      style="flex:1; padding: .75rem; border:0; background:#fff; cursor:pointer; border-right:1px solid #ddd;">
      Privacy
    </button>
    <button class="tab-btn" data-policy="cookies" 
      style="flex:1; padding: .75rem; border:0; background:#f1f1f1; cursor:pointer;">
      Cookies
    </button>
    <button id="popupClose" style="
      padding: .75rem 1rem;
      border:0;
      background:none;
      cursor:pointer;
      font-size: 1.4rem;
      color:#666;
    ">&times;</button>
  `;

  // Body
  const body = document.createElement("div");
  body.style = `
    padding: 1rem 1.25rem;
    overflow-y: auto;
    line-height: 1.6;
  `;
  body.innerHTML = policies.privacy; // default

  // Build popup
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

  // Open on link click
  document.addEventListener("click", e => {
    if (e.target.id === "policy-link") {
      e.preventDefault();
      openPopup();
    }
  });

  // Close button
  document.getElementById("popupClose").onclick = closePopup;

  // Click outside modal closes
  overlay.addEventListener("click", e => {
    if (e.target === overlay) closePopup();
  });

  // Switching tabs
  document.addEventListener("click", e => {
    const btn = e.target.closest(".tab-btn");
    if (!btn) return;

    const type = btn.dataset.policy;
    if (!policies[type]) return;

    // update body
    body.innerHTML = policies[type];

    // update tab visual state
    document.querySelectorAll(".tab-btn").forEach(t =>
      t.classList.remove("active")
    );

    btn.classList.add("active");

    // update button background colors
    document.querySelectorAll(".tab-btn").forEach(b => {
      b.style.background = b.classList.contains("active") ? "#fff" : "#f1f1f1";
    });
  });

})();