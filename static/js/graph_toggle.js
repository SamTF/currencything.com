// Hidding all graphs by default
$('.graph').hide();

// Showing and hiding graphs when you click their corresponding panel
$('.stat-panel').click(function() {
    $(this).find('.graph').toggle(500);
})