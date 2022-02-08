// from Dev Ed youtube video Responsive Navigation Bar Tutorial
// https://www.youtube.com/watch?v=gXkqy0b4M5g
const navSlide = () => {
    const burger = document.querySelector('.burger');
    const nav = document.querySelector('.nav-links');
    const navLinks = document.querySelectorAll('.nav-links li');
    
    // toggle nav
    burger.addEventListener('click',() => {
        nav.classList.toggle('nav-active');
        // animate links
        navLinks.forEach((link,index) => {
            if (link.style.animation){
                link.style.animation ='';
            } else {
                link.style.animation = `navLinkFade 0.5s ease forwards ${index / 7+0.5}s`;
    
            }
            
        });
        // burger animation
        burger.classList.toggle('toggle');
    });
}
    
    
    
navSlide();