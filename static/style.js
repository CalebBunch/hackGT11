function updateSliderBackground(slider) {
    const value = (slider.value - slider.min) / (slider.max - slider.min) * 100;
    slider.style.background = `linear-gradient(to right, #4CAF50 ${value}%, #ddd ${value}%)`;
}

const sliders = document.querySelectorAll(".slider");

sliders.forEach(slider => {
    updateSliderBackground(slider);
    slider.addEventListener("input", () => updateSliderBackground(slider));
});

