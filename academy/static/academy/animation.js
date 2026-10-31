(() => {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduceMotion) return;

  document.documentElement.classList.add('js-motion');

  const reveal = (elements, baseDelay = 0) => {
    elements.forEach((element, index) => {
      element.style.setProperty('--reveal-delay', `${baseDelay + index * 90}ms`);
      observer.observe(element);
    });
  };

  const observer = new IntersectionObserver((entries, currentObserver) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      currentObserver.unobserve(entry.target);
    });
  }, { threshold: 0.12 });

  reveal(Array.from(document.querySelectorAll(
    '.hero-copy > *, .hero-art > *, .hero-bottom > *, .section-heading, .category-chip, .course-card, .cta-inner > *'
  )));

  const codeCard = document.querySelector('.code-card');
  if (codeCard) codeCard.classList.add('code-card-float');
})();
