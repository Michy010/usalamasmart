// The function to toggle the display of Mobile payment block
let PaymentBlock = document.getElementsByClassName ('mobile-payment-processing-div')[0];
let BankPaymentBlock = document.getElementsByClassName ('bank-payment-processing-div')[0];
let showButton = document.getElementById ('mobile-content-block');
let showBankBlock = document.getElementById ('bank-content-block');

function showPaymentBlock () {
    
    PaymentBlock.style.display = 'flex';
    BankPaymentBlock.style.display = 'none';
}

showButton.addEventListener('click' , showPaymentBlock)

// The function to toggle the  display of Bank payment block
function showBankPaymentBlock() {
    BankPaymentBlock.style.display = 'flex';
    PaymentBlock.style.display = 'none';
}

showBankBlock.addEventListener('click', showBankPaymentBlock)

