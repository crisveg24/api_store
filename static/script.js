// /static/script.js
function fetchStores() {
    fetch('http://localhost:5000/stores')
        .then(response => response.json())
        .then(data => {
            const storeList = document.getElementById('store-list');
            storeList.innerHTML = '';  // Limpiar lista antes de agregar nuevos elementos
            data.forEach(store => {
                const listItem = document.createElement('li');
                listItem.textContent = `Tienda ${store.store_id} - Área: ${store.store_area} m²`;
                storeList.appendChild(listItem);
            });
        })
        .catch(error => console.error('Error fetching stores:', error));
}
