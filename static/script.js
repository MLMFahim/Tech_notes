function highlightCard(element) {
    // Basic interaction: toggle a background color when clicked
    const allCards = document.querySelectorAll('.card');
    allCards.forEach(card => card.style.backgroundColor = "white");
    
    element.style.backgroundColor = "#e1f5fe";
    console.log("Viewing notes for: " + element.querySelector('h2').innerText);
}


function copyToClipboard(btn) {
    const code = btn.parentElement.nextElementSibling.innerText;
    navigator.clipboard.writeText(code);
    btn.innerText = "Copied!";
    setTimeout(() => { btn.innerText = "Copy"; }, 2000);
}
