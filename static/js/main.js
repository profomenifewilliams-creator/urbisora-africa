(() => {
  "use strict";

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const root = document.documentElement;
  root.classList.add("js-ready");

  // Mobile menu: no framework, with accessible state.
  const menuToggle = document.querySelector("[data-menu-toggle]");
  const mainNav = document.querySelector("[data-main-nav]");
  if (menuToggle && mainNav) {
    menuToggle.addEventListener("click", () => {
      const open = menuToggle.getAttribute("aria-expanded") === "true";
      menuToggle.setAttribute("aria-expanded", String(!open));
      mainNav.classList.toggle("is-open", !open);
      document.body.classList.toggle("nav-open", !open);
    });
    mainNav.querySelectorAll("a").forEach(link => link.addEventListener("click", () => {
      menuToggle.setAttribute("aria-expanded", "false");
      mainNav.classList.remove("is-open");
      document.body.classList.remove("nav-open");
    }));
  }

  // Small reading-progress line gives long pages a quiet sense of orientation.
  const progress = document.querySelector("[data-reading-progress]");
  const updateProgress = () => {
    if (!progress) return;
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    const amount = scrollable > 0 ? Math.min(100, Math.max(0, window.scrollY / scrollable * 100)) : 0;
    progress.style.transform = `scaleX(${amount / 100})`;
  };
  window.addEventListener("scroll", updateProgress, { passive: true });
  updateProgress();

  // Reveal sections on entry. With reduced motion enabled, content remains visible.
  const revealItems = document.querySelectorAll(".feature, .property-card, .panel, .realtor-card, .detail-description, .form-card, .empty-state");
  if ("IntersectionObserver" in window && !reduceMotion) {
    revealItems.forEach((el, index) => {
      el.classList.add("reveal-on-scroll");
      el.style.setProperty("--reveal-delay", `${Math.min(index % 3, 2) * 70}ms`);
    });
    const revealObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-revealed");
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: "0px 0px -35px 0px" });
    revealItems.forEach(el => revealObserver.observe(el));
  }

  // Canvas: lightweight abstract African city / property-network visual. It is
  // decorative, stays behind hero copy, and stops animating off-screen.
  const canvas = document.querySelector("[data-hero-visual]");
  const hero = canvas && canvas.closest(".hero");
  if (canvas && hero) {
    const ctx = canvas.getContext("2d", { alpha: true });
    if (ctx) {
      let width = 0, height = 0, dpr = 1, raf = 0, visible = true, pointerX = 0.5, pointerY = 0.42, tick = 0;
      const nodes = [];
      const resize = () => {
        const rect = hero.getBoundingClientRect();
        width = Math.max(1, rect.width);
        height = Math.max(1, rect.height);
        dpr = Math.min(window.devicePixelRatio || 1, 1.7);
        canvas.width = Math.round(width * dpr);
        canvas.height = Math.round(height * dpr);
        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        nodes.length = 0;
        const cols = Math.max(6, Math.min(13, Math.round(width / 105)));
        const rows = Math.max(4, Math.min(8, Math.round(height / 90)));
        for (let row = 0; row < rows; row++) {
          for (let col = 0; col < cols; col++) {
            nodes.push({
              x: (col + 0.25 + Math.random() * 0.5) / cols * width,
              y: (row + 0.25 + Math.random() * 0.5) / rows * height,
              phase: Math.random() * Math.PI * 2,
              radius: 0.7 + Math.random() * 1.7
            });
          }
        }
      };
      const draw = () => {
        if (!visible || document.hidden) return;
        ctx.clearRect(0, 0, width, height);
        const shiftX = (pointerX - 0.5) * 15;
        const shiftY = (pointerY - 0.5) * 12;
        // Fine architectural grid.
        ctx.lineWidth = 0.6;
        ctx.strokeStyle = "rgba(205, 229, 190, 0.075)";
        const step = 44;
        for (let x = 0; x < width; x += step) {
          ctx.beginPath(); ctx.moveTo(x + shiftX * 0.15, 0); ctx.lineTo(x + shiftX * 0.15, height); ctx.stroke();
        }
        for (let y = 0; y < height; y += step) {
          ctx.beginPath(); ctx.moveTo(0, y + shiftY * 0.15); ctx.lineTo(width, y + shiftY * 0.15); ctx.stroke();
        }
        // Contour arcs evoke land surveys and site plans.
        const ox = width * (0.73 + (pointerX - 0.5) * 0.035);
        const oy = height * (0.49 + (pointerY - 0.5) * 0.04);
        for (let i = 0; i < 9; i++) {
          ctx.beginPath();
          ctx.ellipse(ox, oy, 85 + i * 28, 48 + i * 20, -0.26, 0, Math.PI * 2);
          ctx.strokeStyle = `rgba(190, 220, 170, ${0.085 - i * 0.006})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
        // Abstract skyline outlines, drawn from normalized coordinates.
        const baseY = height * 0.86;
        const buildings = [
          [0.52, .17, .23], [0.56, .10, .42], [0.60, .12, .32], [0.64, .08, .53],
          [0.68, .15, .39], [0.73, .11, .63], [0.78, .14, .44], [0.83, .10, .33],
          [0.87, .16, .52], [0.92, .12, .29], [0.97, .15, .4]
        ];
        buildings.forEach(([x, w, h], i) => {
          const bx = x * width + shiftX * (0.35 + i * 0.015);
          const bh = h * height;
          ctx.beginPath();
          ctx.moveTo(bx, baseY);
          ctx.lineTo(bx, baseY - bh);
          ctx.lineTo(bx + w * width, baseY - bh);
          ctx.lineTo(bx + w * width, baseY);
          ctx.strokeStyle = "rgba(197, 225, 180, 0.25)";
          ctx.lineWidth = 1;
          ctx.stroke();
          if (w * width > 17) {
            for (let wy = baseY - bh + 13; wy < baseY - 7; wy += 17) {
              ctx.beginPath(); ctx.moveTo(bx + 5, wy); ctx.lineTo(bx + w * width - 5, wy);
              ctx.strokeStyle = "rgba(197, 225, 180, 0.15)"; ctx.stroke();
            }
          }
        });
        // Network lines only between nearby points.
        nodes.forEach((a, i) => {
          nodes.slice(i + 1).forEach(b => {
            const dx = a.x - b.x, dy = a.y - b.y, distance = Math.hypot(dx, dy);
            if (distance < 112) {
              ctx.beginPath(); ctx.moveTo(a.x + shiftX, a.y + shiftY); ctx.lineTo(b.x + shiftX, b.y + shiftY);
              ctx.strokeStyle = `rgba(206, 231, 190, ${0.12 * (1 - distance / 112)})`; ctx.lineWidth = .8; ctx.stroke();
            }
          });
        });
        nodes.forEach(n => {
          const pulse = 0.65 + (Math.sin(tick * 0.025 + n.phase) + 1) * 0.33;
          ctx.beginPath(); ctx.arc(n.x + shiftX, n.y + shiftY, n.radius * pulse, 0, Math.PI * 2);
          ctx.fillStyle = "rgba(210, 235, 190, 0.65)"; ctx.fill();
        });
        tick++;
        if (!reduceMotion) raf = requestAnimationFrame(draw);
      };
      if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver(entries => {
          visible = entries[0].isIntersecting;
          if (visible) {
            cancelAnimationFrame(raf);
            draw();
          } else cancelAnimationFrame(raf);
        }, { threshold: 0.01 });
        observer.observe(hero);
      }
      hero.addEventListener("pointermove", event => {
        const rect = hero.getBoundingClientRect();
        pointerX = (event.clientX - rect.left) / rect.width;
        pointerY = (event.clientY - rect.top) / rect.height;
        if (reduceMotion) draw();
      }, { passive: true });
      hero.addEventListener("pointerleave", () => { pointerX = 0.5; pointerY = 0.42; if (reduceMotion) draw(); });
      window.addEventListener("resize", () => { resize(); if (reduceMotion) draw(); }, { passive: true });
      document.addEventListener("visibilitychange", () => {
        if (!document.hidden && visible) draw();
        else cancelAnimationFrame(raf);
      });
      resize();
      draw();
    }
  }

  // Gentle card tilt on desktop. Disabled for touch or reduced-motion users.
  if (!reduceMotion && window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
    document.querySelectorAll(".property-card, .realtor-card").forEach(card => {
      card.addEventListener("pointermove", event => {
        const rect = card.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width - 0.5;
        const y = (event.clientY - rect.top) / rect.height - 0.5;
        card.style.setProperty("--tilt-x", `${(-y * 2.4).toFixed(2)}deg`);
        card.style.setProperty("--tilt-y", `${(x * 2.4).toFixed(2)}deg`);
      });
      card.addEventListener("pointerleave", () => {
        card.style.setProperty("--tilt-x", "0deg");
        card.style.setProperty("--tilt-y", "0deg");
      });
    });
  }

  // Polished filter clear button and live search labels.
  document.querySelectorAll(".search-form input, .search-form select").forEach(field => {
    field.addEventListener("change", () => field.classList.toggle("has-value", String(field.value || "").length > 0));
  });

  // Avoid stale animated state when the browser navigates back/forward.
  window.addEventListener("pageshow", () => {
    document.body.classList.remove("nav-open");
    if (menuToggle) menuToggle.setAttribute("aria-expanded", "false");
    if (mainNav) mainNav.classList.remove("is-open");
  });
})();
