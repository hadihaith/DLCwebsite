document.addEventListener('DOMContentLoaded', function() {
  // Find all calendar content elements
  const calendarContents = document.querySelectorAll('.sui-calendar-content');
  
  calendarContents.forEach(content => {
    const fromDateEl = content.querySelector('.from_date');
    const toDateEl = content.querySelector('.to_date');
    
    // Clean up any text nodes between elements
    Array.from(content.childNodes).forEach(node => {
      if (node.nodeType === 3 && node.textContent.trim() === '') {
        content.removeChild(node);
      }
    });
    
    if (fromDateEl && toDateEl) {
      // This is a date range
      fromDateEl.classList.add('date-from');
      toDateEl.classList.add('date-to');
      content.classList.add('date-range');
    } else if (fromDateEl && !toDateEl) {
      // This is a single date
      fromDateEl.classList.add('single-date');
    }
  });
});