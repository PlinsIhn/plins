/* script 1 */

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('.collapse').forEach(collapseEl => {
      const id = collapseEl.getAttribute('id'); // id = collapseDetailsXX
      const zoneId = id.replace('collapseDetails', '');
      const icon = document.getElementById('icon_zone' + zoneId);

      collapseEl.addEventListener('show.bs.collapse', () => {
        if (icon) {
          icon.classList.remove('fa-eye-slash');
          icon.classList.add('fa-eye');
        }
      });

      collapseEl.addEventListener('hide.bs.collapse', () => {
        if (icon) {
          icon.classList.remove('fa-eye');
          icon.classList.add('fa-eye-slash');
        }
      });
    });
  });
