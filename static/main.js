document.addEventListener("DOMContentLoaded", () => {
  console.log("Eduvil Dream Logic Portal Loaded!");
  
  // Initialize button interactions
  initializeButtons();
  
  // Initialize responsive features
  initializeResponsiveFeatures();
  
  // Add loading animation
  addLoadingAnimation();
});

function initializeButtons() {
  const buttons = document.querySelectorAll(".app-button");
  
  buttons.forEach(btn => {
    // Click event with enhanced feedback
    btn.addEventListener("click", (e) => {
      console.log(`${btn.textContent.trim()} clicked`);
      
      // Add visual feedback
      btn.style.transform = "scale(0.95)";
      setTimeout(() => {
        btn.style.transform = "";
      }, 150);
    });
    
    // Enhanced hover effects for desktop
    if (!isMobileDevice()) {
      btn.addEventListener("mouseenter", () => {
        const icon = btn.querySelector(".icon");
        if (icon) {
          icon.style.transform = "scale(1.1) rotate(5deg)";
        }
      });
      
      btn.addEventListener("mouseleave", () => {
        const icon = btn.querySelector(".icon");
        if (icon) {
          icon.style.transform = "scale(1) rotate(0deg)";
        }
      });
    }
    
    // Touch events for mobile
    btn.addEventListener("touchstart", (e) => {
      btn.style.transform = "scale(0.98)";
    });
    
    btn.addEventListener("touchend", (e) => {
      setTimeout(() => {
        btn.style.transform = "";
      }, 100);
    });
  });
}

function initializeResponsiveFeatures() {
  // Handle orientation changes on mobile
  window.addEventListener("orientationchange", () => {
    setTimeout(() => {
      adjustLayoutForOrientation();
    }, 100);
  });
  
  // Handle window resize
  let resizeTimeout;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
      adjustLayoutForScreenSize();
    }, 250);
  });
  
  // Initial layout adjustment
  adjustLayoutForScreenSize();
}

function addLoadingAnimation() {
  const container = document.querySelector(".container");
  const buttons = document.querySelectorAll(".app-button");
  
  // Add fade-in animation
  container.style.opacity = "0";
  container.style.transform = "translateY(20px)";
  
  setTimeout(() => {
    container.style.transition = "all 0.6s ease";
    container.style.opacity = "1";
    container.style.transform = "translateY(0)";
  }, 100);
  
  // Stagger button animations
  buttons.forEach((btn, index) => {
    btn.style.opacity = "0";
    btn.style.transform = "translateY(30px)";
    
    setTimeout(() => {
      btn.style.transition = "all 0.5s ease";
      btn.style.opacity = "1";
      btn.style.transform = "translateY(0)";
    }, 300 + (index * 150));
  });
}

function adjustLayoutForOrientation() {
  const container = document.querySelector(".container");
  const isLandscape = window.innerWidth > window.innerHeight;
  
  if (isMobileDevice() && isLandscape) {
    container.style.padding = "20px";
  } else if (isMobileDevice()) {
    container.style.padding = "30px 20px";
  }
}

function adjustLayoutForScreenSize() {
  const buttonGrid = document.querySelector(".button-grid");
  const screenWidth = window.innerWidth;
  
  // Adjust grid layout based on screen size
  if (screenWidth < 480) {
    buttonGrid.style.gap = "15px";
  } else if (screenWidth < 768) {
    buttonGrid.style.gap = "20px";
  } else {
    buttonGrid.style.gap = "30px";
  }
  
  // Adjust icon transitions for mobile performance
  const icons = document.querySelectorAll(".icon");
  icons.forEach(icon => {
    if (isMobileDevice()) {
      icon.style.transition = "transform 0.2s ease";
    } else {
      icon.style.transition = "transform 0.3s ease";
    }
  });
}

function isMobileDevice() {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) 
    || window.innerWidth <= 768;
}

// Add intersection observer for animations when scrolling (future use)
function initializeScrollAnimations() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px"
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("animate-in");
      }
    });
  }, observerOptions);
  
  // Observe elements for future scroll animations
  const animateElements = document.querySelectorAll(".app-button");
  animateElements.forEach(el => observer.observe(el));
}

// Initialize scroll animations if needed
// initializeScrollAnimations();
