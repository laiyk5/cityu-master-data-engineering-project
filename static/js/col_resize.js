/*
 * Lightweight column resizer for tables.
 * Usage: will attach a vertical resizer handle to each TH in the first header row.
 * Behavior: dragging the handle resizes that column's width (applies inline width to TH and every TD in that column index).
 */

document.addEventListener('DOMContentLoaded', function () {
  const table = document.querySelector('.articles-table');
  if (!table) return;

  // make table layout fixed to avoid header/content width jitter
  table.style.tableLayout = table.style.tableLayout || 'fixed';

  const ths = table.querySelectorAll('thead th');
  ths.forEach((th, index) => {
    // skip non-resizable columns if they have data-no-resize attribute
    if (th.dataset.noResize === '1') return;

    // create handle
    const resizer = document.createElement('div');
    resizer.className = 'th-resizer';
    th.style.position = 'relative';
    th.appendChild(resizer);

    // initial width if not set: compute current width
    if (!th.style.width) {
      const w = th.getBoundingClientRect().width;
      th.style.width = Math.max(60, Math.round(w)) + 'px';
    }

    let startX, startWidth;

    const mousemove = (e) => {
      if (startX == null) return;
      const dx = e.clientX - startX;
      const newWidth = Math.max(50, startWidth + dx);
      th.style.width = newWidth + 'px';

      // apply to all cells in this column index
      const rows = table.querySelectorAll('tbody tr');
      rows.forEach(row => {
        const cells = row.children;
        // guard: skip if index exceeds available cells
        if (index < cells.length) {
          cells[index].style.width = newWidth + 'px';
        }
      });
    };

    const mouseup = () => {
      startX = null;
      startWidth = null;
      document.removeEventListener('mousemove', mousemove);
      document.removeEventListener('mouseup', mouseup);
      document.body.style.cursor = '';
    };

    resizer.addEventListener('mousedown', (e) => {
      e.preventDefault();
      startX = e.clientX;
      startWidth = th.getBoundingClientRect().width;
      document.addEventListener('mousemove', mousemove);
      document.addEventListener('mouseup', mouseup);
      document.body.style.cursor = 'col-resize';
    });
  });
});
