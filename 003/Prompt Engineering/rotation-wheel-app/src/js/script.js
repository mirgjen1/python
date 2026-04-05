// This file contains the JavaScript code that implements the rotation wheel functionality.

const names = ['Alice', 'Bob']; // Array of names to choose from
const wheel = document.getElementById('wheel'); // Reference to the wheel element
const spinButton = document.getElementById('spin-button'); // Reference to the spin button
const resultDisplay = document.getElementById('result'); // Reference to the result display

spinButton.addEventListener('click', spinWheel);

function spinWheel() {
    const randomDegree = Math.floor(Math.random() * 360) + 720; // Random degree for spinning
    wheel.style.transition = 'transform 4s ease-out'; // Set transition for smooth spinning
    wheel.style.transform = `rotate(${randomDegree}deg)`; // Rotate the wheel

    setTimeout(() => {
        const selectedIndex = Math.floor((randomDegree % 360) / (360 / names.length)); // Determine selected name
        resultDisplay.textContent = `Selected: ${names[selectedIndex]}`; // Display the selected name
    }, 4000); // Wait for the spinning animation to finish
}