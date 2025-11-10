    /* script 1 */
document.addEventListener("DOMContentLoaded", function () {
    const carousel = document.querySelector('#carouselProduitComplet');
    const items = carousel.querySelectorAll('.carousel-item');
    const counter = document.getElementById('carouselCounter');
    const thumbnails = document.querySelectorAll('.miniature-image');
    const total = items.length;

    // Initialisation du carrousel avec cycle désactivé
    const mainCarousel = new bootstrap.Carousel(carousel, {
        wrap: false,
        interval: false
    });

    // Mettre à jour le compteur
    function updateCounter(index) {
        counter.textContent = `${index + 1} / ${total}`;
    }

    // Gérer les miniatures actives
    function updateThumbnailActive(index) {
        thumbnails.forEach((thumb, i) => {
            thumb.classList.toggle('border-primary', i === index);
        });
    }

    // Initialisation
    updateCounter(0);
    updateThumbnailActive(0);

    // Écouteur pour les slides manuels (glissement)
    carousel.addEventListener('slide.bs.carousel', function (event) {
        updateCounter(event.to);
        updateThumbnailActive(event.to);
    });

    // Nouveau : Gestion des clics sur miniatures pour saut direct
    thumbnails.forEach((thumbnail, index) => {
        thumbnail.addEventListener('click', (e) => {
            e.preventDefault();
            mainCarousel.to(index); // Saut direct à l'image cible
            updateCounter(index);
            updateThumbnailActive(index);
        });
    });
});


      /*  script  2  */
/* script 2 */
document.addEventListener('DOMContentLoaded', function() {
  const images = document.querySelectorAll('#carouselProduitComplet .carousel-item img');
  const modalCarouselInner = document.getElementById('modalCarouselInner');
  const modal = new bootstrap.Modal(document.getElementById('imageModal'));
  const totalImages = images.length;

  // Création du compteur pour le modal
  const modalCounter = document.createElement('div');
  modalCounter.className = 'position-absolute bottom-0 end-0 mb-2 me-2 bg-secondary text-white px-2 py-1 rounded';
  modalCounter.style.fontSize = '0.7em';
  modalCounter.style.zIndex = '10';
  modalCounter.innerHTML = `1 / ${totalImages}`;
  modalCarouselInner.parentElement.appendChild(modalCounter);

  // Désactivation auto-défilement
  const modalCarousel = document.getElementById('modalCarousel');
  modalCarousel.setAttribute('data-bs-interval', 'false');

  const imagesData = Array.from(images).map(img => ({
    src: img.src,
    alt: img.alt || 'Image agrandie'
  }));

  modalCarouselInner.innerHTML = imagesData.map((imgData, index) => `
    <div class="carousel-item ${index === 0 ? 'active' : ''}">
      <img src="${imgData.src}" class="d-block mx-auto rounded" alt="${imgData.alt}" style="max-height: 80vh; width: auto; max-width: 100%;">
    </div>
  `).join('');

  // Initialisation du carrousel modal
  const carousel = new bootstrap.Carousel(modalCarousel, {
    interval: false,
    wrap: false
  });

  // Mise à jour du compteur modal
  modalCarousel.addEventListener('slide.bs.carousel', function(event) {
    modalCounter.innerHTML = `${event.to + 1} / ${totalImages}`;
  });

  // Gestion des clics sur images
  images.forEach((img, index) => {
    img.style.cursor = 'pointer';
    img.addEventListener('click', () => {
      carousel.to(index); // Aller directement au slide correspondant
      modalCounter.innerHTML = `${index + 1} / ${totalImages}`; // Mettre à jour le compteur
      modal.show();
    });
  });
});