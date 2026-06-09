(function(){
  'use strict';
  if(!window.IntersectionObserver) return;

  // Targets to animate on scroll
  var selectors = [
    '.section',
    '.lane-card',
    '.who-help-card',
    '.testimonial-mini',
    '.testimonial-card',
    '.stats-bar',
    '.step',
    '.blog-card',
    '.city-photo',
    '.info-card',
    '.sidebar-card',
    '.compare-table',
    '.post-cta'
  ].join(',');

  var obs = new IntersectionObserver(function(entries){
    entries.forEach(function(entry){
      if(entry.isIntersecting){
        entry.target.classList.add('visible');
        obs.unobserve(entry.target);
      }
    });
  },{threshold:0.08,rootMargin:'0px 0px -30px 0px'});

  // Add .anim class and observe each element
  var els = document.querySelectorAll(selectors);
  els.forEach(function(el, i){
    // Skip elements already above the fold on load
    var rect = el.getBoundingClientRect();
    if(rect.top < window.innerHeight * 0.85){
      // Already visible — no animation needed
      return;
    }
    el.classList.add('anim');
    // Stagger children of grids
    if(i % 3 === 1) el.classList.add('anim-delay-1');
    if(i % 3 === 2) el.classList.add('anim-delay-2');
    obs.observe(el);
  });
})();
