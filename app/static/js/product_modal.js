function openAddProductModal() {
    const modal = document.getElementById("productModal");
    const form = document.getElementById("productForm");

    document.getElementById("modalTitle").innerText = "Add Product";
    form.action = "/products/add";

    modal.style.display = "block";
}

function openEditProductModal(productId) {
    const modal = document.getElementById("productModal");
    const form = document.getElementById("productForm");

    document.getElementById("modalTitle").innerText = "Edit Product";
    form.action = `/products/edit/${productId}`;

    modal.style.display = "block";
}

function closeProductModal() {
    document.getElementById("productModal").style.display = "none";
}