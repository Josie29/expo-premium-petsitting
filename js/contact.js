const form = document.querySelector("[data-contact-form]");
const statusMessage = document.querySelector("[data-contact-status]");

if (form && statusMessage) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    statusMessage.textContent = "Sending your request...";
    statusMessage.dataset.state = "pending";

    const endpoint = form.dataset.endpoint;
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorPayload = await response.json().catch(() => ({}));
        throw new Error(errorPayload.detail || "Unable to send your message.");
      }

      form.reset();
      statusMessage.textContent = "Thanks! We'll reply within 24 hours.";
      statusMessage.dataset.state = "success";
    } catch (error) {
      statusMessage.textContent = error.message;
      statusMessage.dataset.state = "error";
    }
  });
}
