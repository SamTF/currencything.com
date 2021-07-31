//// BUTTONS that filter the time period for the displayed Blockchain Statistics (does not affect graphs)
// Using:   Python to get the blockchain data at each time period
//          JQuery to get the Python data, and to update the statistics text


$('button').click(function(event) {
    // prints the ID of the button that was clicked
    console.log(event.target.id)

    // checking if the button is already selected to avoid unecessary flask calls
    if ($(this).hasClass('selected')) {
        console.log("Button is already selected. Doing Nothing.")
        return
    }

    // Removing selected class from other elements
    $('.selected').removeClass('selected')

    // Adding the selected class to the button
    $(this).addClass('selected')

    // Receives AND sends data to Python!
    $.getJSON({
        url: "/update_stats",                               // The Flask route that calls the desired Python function
        data: { period: event.target.id },                  // Passing a parameter to specify the time period
        success: function(data){
            console.table(data);
            refresh_stats(data);                            // Calling a JQuery function to update the text elements with the new data
            // $('button').text(data.x);
        }
    });
})

// Updating all the stats text elements with the new data
function refresh_stats(data) {
    $('#stats-supply').     text(data.supply);
    $('#stats-mined').      text(data.mined);
    $('#stats-trades').     text(data.trades);
    $('#stats-user_trades').text(data.user_trades);
    $('#stats-user_num').   text(data.user_num);
    $('#stats-biggest').    text(data.biggest);
    $('span').              text(data.text);
}



//// OLD FUNCTIONS that could be useful for something later
// Function with parameters = Works at sending data perfectly, but cannot receive data
    // $.getJSON('/background_process_test/' + event.target.id),
    //     function(data) {
    //         console.log(data);
    //         $('button').text(data.a);
    //     };
    
    // Receives the data returned by Python, but cannot send data
    // $.getJSON({
    //     url: "/get_json",
    //     success: function(data){
    //         console.table(data);
    //         $('button').text(data.a);
    //     }
    // });