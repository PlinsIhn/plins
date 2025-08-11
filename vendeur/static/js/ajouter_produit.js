
/*  script 0 */

  function onlyDigits(event) {
    const allowedKeys = ['Backspace', 'ArrowLeft', 'ArrowRight', 'Tab', 'Delete'];
    const isDigit = /^[0-9]$/.test(event.key);

    // Autoriser uniquement chiffres et touches de contrôle
    if (isDigit || allowedKeys.includes(event.key)) {
      return true;
    }

    // Bloquer tout le reste (lettres, ., -, e, etc.)
    event.preventDefault();
    return false;
  }


/* script 1 */

  function previewImage(event) {
    const input = event.target;
    const previewContainer = document.getElementById('preview-container');
    const previewImage = document.getElementById('preview-image');

    if (input.files && input.files[0]) {
      const reader = new FileReader();

      reader.onload = function(e) {
        previewImage.src = e.target.result;
        previewContainer.style.display = 'block';
      }

      reader.readAsDataURL(input.files[0]);
    } else {
      previewContainer.style.display = 'none';
      previewImage.src = '#';
    }
  }
  
/* script 2 */
  /*  script 2 prix */
function formatNumberInput(input) {
  let rawValue = input.value.replace(/\D/g, '');
  let formattedValue = rawValue.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  input.value = formattedValue;
}

document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('form');
  if (form) {
    form.addEventListener('submit', function () {
      const prixInputs = document.querySelectorAll('input[name$="-prix"], input[name="prix"]');
      prixInputs.forEach(function (input) {
        input.value = input.value.replace(/\s/g, '');
      });
    });
  }
});

/* script 3 */

document.addEventListener('DOMContentLoaded', function () {
  // Délégation d’événement pour capter tous les input image-variation
  document.body.addEventListener('change', function(event) {
    if (event.target.classList.contains('image-variation-input')) {
      const input = event.target;
      const container = input.closest('.col-md-6');
      const previewContainer = container.querySelector('.preview-container');
      const previewImage = container.querySelector('.preview-image');

      if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
          previewImage.src = e.target.result;
          previewContainer.style.display = 'block';
        }
        reader.readAsDataURL(input.files[0]);
      } else {
        previewImage.src = '#';
        previewContainer.style.display = 'none';
      }
    }
  });
});


/* script 7 */

  const inputDetailImage = document.getElementById('id_detaille_image');
  const previewContainer = document.getElementById('detail-preview-container');

  // Pour stocker les fichiers sélectionnés
  let selectedFiles = [];

  inputDetailImage.addEventListener('change', function (event) {
    const files = Array.from(event.target.files);
    selectedFiles = [...selectedFiles, ...files];

    // Efface l'aperçu actuel
    previewContainer.innerHTML = '';

    selectedFiles.forEach((file, index) => {
      const reader = new FileReader();
      reader.onload = function (e) {
        const wrapper = document.createElement('div');
        wrapper.classList.add('preview-image-wrapper');

        const img = document.createElement('img');
        img.src = e.target.result;
        img.classList.add('preview-image');

        const removeBtn = document.createElement('button');
        removeBtn.innerText = '×';
        removeBtn.classList.add('remove-btn');
        removeBtn.addEventListener('click', function () {
          selectedFiles.splice(index, 1); // Supprimer le fichier sélectionné
          updateInputFiles();
          wrapper.remove(); // Supprimer l'aperçu
        });

        wrapper.appendChild(img);
        wrapper.appendChild(removeBtn);
        previewContainer.appendChild(wrapper);
      };
      reader.readAsDataURL(file);
    });

    updateInputFiles();
  });

  function updateInputFiles() {
    const dataTransfer = new DataTransfer();
    selectedFiles.forEach(file => dataTransfer.items.add(file));
    inputDetailImage.files = dataTransfer.files;
  }


  