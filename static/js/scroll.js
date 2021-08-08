// SMOOTHLY SCROLLS the webpage to the specified div WITHOUT changing the URL!

// The scrolling function; from: https://stackoverflow.com/questions/15223006/scroll-with-anchor-without-in-url
function scroll(anchor) {
    document.getElementById(anchor).scrollIntoView(true);
}

$("#scroll-up").click(function() {
    scroll('top');
})

$("#scroll-down").click(function() {
    scroll('bottom');
})