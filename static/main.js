document.addEventListener("DOMContentLoaded", () => {
  console.log("Unified Portal Loaded!");
  const buttons = document.querySelectorAll(".app-button");
  buttons.forEach(btn => {
    btn.addEventListener("click", () => {
      console.log(`${btn.textContent} clicked`);
    });
  });
});
