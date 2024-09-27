
//navigation toggle button and responsive navbar
var myToggle = document.querySelector('.mynav-toggle');
var itemsLeft = document.querySelector('.mynav-items-left');
var itemsRight = document.querySelector('.mynav-items-right');
var myForm = document.querySelector('.mynav-form');

function handleViewportChange() {
if (window.innerWidth <= 950) {
    itemsLeft.style.display = 'none';
    itemsRight.style.display = 'none';
    myForm.style.display = 'none';
} else {
    itemsLeft.style.display = 'flex';
    itemsRight.style.display = 'flex';
    myForm.style.display = 'initial';
}
}

myToggle.addEventListener('click', function() {
if (window.innerWidth <= 950) {
    if (itemsLeft.style.display === 'none') {
    itemsLeft.style.display = 'flex';
    itemsRight.style.display = 'flex';
    myForm.style.display = 'initial';
    } else {
    itemsLeft.style.display = 'none';
    itemsRight.style.display = 'none';
    myForm.style.display = 'none';
    }
}
});

window.addEventListener('resize', handleViewportChange);

document.addEventListener('click', function(event) {
if (window.innerWidth <= 950 && !event.target.closest('.mynav-container')) {
    itemsLeft.style.display = 'none';
    itemsRight.style.display = 'none';
    myForm.style.display = 'none';
}
});

// Call the function initially to set the initial state
handleViewportChange();
