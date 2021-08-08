// PLAYS SFX when people click on things

// All the sound effect files
var sfx_click1      = new Audio('/static/sfx/click1.ogg');
var sfx_click2      = new Audio('/static/sfx/click2.ogg');
var sfx_scroll_down = new Audio('/static/sfx/filesspill1.mp3');
var sfx_scroll_up   = new Audio('/static/sfx/filesspill2.mp3');
var sfx_open        = new Audio('/static/sfx/openwindow.ogg');
var sfx_close        = new Audio('/static/sfx/close.ogg');

// Alternate playing clicking sounds
var clicks = [sfx_click1, sfx_click2]
var click_count = 0;
$(document).click(function() {
    click_count++;
    var i = click_count % 2;
    clicks[i].play();
});

// Scroll buttons
$("#scroll-down").click(function() {
    sfx_scroll_down.play()
})
$("#scroll-up").click(function() {
    sfx_scroll_up.play()
})

// Opening/Closing stat panel
var open_close = [sfx_open, sfx_close]
var open_count = 1;
$(".stat-panel").click(function() {
    // sfx_open.play()

    open_count++;
    var i = open_count % 2;
    open_close[i].play();

    var panel = $(this).text()
})