let PaymentBlock = document.getElementsByClassName ('mobile-payment-processing-div')[0];

    let showButton = document.getElementById ('mobile-content-block');
    

    function showPaymentBlock () {
        PaymentBlock.style.display = 'flex';
    }

showButton.addEventListener('click' , showPaymentBlock)
