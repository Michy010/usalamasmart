function activateBorder (element) {
    document.querySelectorAll('.payment-section ul li').forEach(li => {
        li.classList.remove('active');
    })
    element.classList.add ('active');
}