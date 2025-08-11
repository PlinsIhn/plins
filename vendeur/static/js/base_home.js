    function toggleContact() {
        const contactDiv = document.getElementById("contact-info");
        const icon = document.getElementById("chevron-icon");
        
        const isVisible = contactDiv.classList.contains("open");
        if (isVisible) {
        contactDiv.classList.remove("open");
        } else {
        contactDiv.classList.add("open");
        }
        
        icon.classList.toggle("fa-chevron-down", isVisible);
        icon.classList.toggle("fa-chevron-up", !isVisible);
    }