// --- Service Worker Registration ---
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/user/plugin/optimizer/service-worker.js", { scope: "/" })
      .then(registration => {
        console.log("Optimizer Plugin: Service Worker registered successfully.", registration);
      })
      .catch(registrationError => {
        console.log("Optimizer Plugin: Service Worker registration failed.", registrationError);
      });
  });
}
