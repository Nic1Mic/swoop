const heartButtons = document.querySelectorAll(".heart-btn");

heartButtons.forEach((button) => {
    button.addEventListener("click", () => {
        const icon = button.querySelector("i");
        icon.classList.toggle("bi-heart");
        icon.classList.toggle("bi-heart-fill");
    });
});
const imageInput = document.getElementById("imageInput");
const previewBox = document.getElementById("previewBox");

if (imageInput && previewBox) {
    imageInput.addEventListener("change", () => {
        const file = imageInput.files[0];

        if (!file) {
            previewBox.innerHTML = "<p>No image selected yet</p>";
            return;
        }

        const reader = new FileReader();

        reader.onload = (event) => {
            previewBox.innerHTML = `<img src="${event.target.result}" alt="Listing preview">`;
        };

        reader.readAsDataURL(file);
    });
}

const descriptionInput = document.getElementById("descriptionInput");
const charCount = document.getElementById("charCount");

if (descriptionInput && charCount) {
    descriptionInput.addEventListener("input", () => {
        charCount.textContent = `${descriptionInput.value.length} / 500`;
    });
}

document.querySelectorAll(".product-card form").forEach((form) => {
    form.addEventListener("click", function(event) {
        event.stopPropagation();
    });
});

document.querySelectorAll(".wishlist-form").forEach((form) => {
    form.addEventListener("click", function(event) {
        event.preventDefault();
        event.stopPropagation();
        form.submit();
    });
});

document.addEventListener("click", function(event) {
    const wishlistForm = event.target.closest(".wishlist-form");

    if (wishlistForm) {
        event.preventDefault();
        event.stopPropagation();
        wishlistForm.submit();
    }
});
