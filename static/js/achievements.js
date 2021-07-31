//// FLAWLESS Method to highlight achievement milestones!
// Using:   Python to get the achievement data
//          JQuery to read the python data, and add the Achievement class to the matching table rows


var table = $(".table-container");                      // getting the table
var row_count = $(".table-container tr").length -1;     // getting amount of rows in table (minus 1 because it starts at 0)

// Getting the Achievement Milestone & Trade ID values from Python as an array : [ACHIEVEMENT, TRADE ID]
$.getJSON({
        url: "/get_achievements",                       // the app.route from Flask that routes to the desired Python function
        success: function(data){
            // Highlighting each achievement in the HTML data using this data
            data.forEach(item => highlight_achievement(item));
        }
    });

// Adds the Achievement CSS class to every milestone trade by checking their index in the HTML table and giving them a specific tooltip description!
function highlight_achievement(item) {
    achievement = item[0];
    trade_id    = item[1];

    index = row_count - trade_id;                       // since the table is in reverse, we must reverse the index too
    row = table.find('tr').eq(index);                   // finds the row with matching corrected index
    row.addClass("achievement");                        // adds the achievement css class
    
    desc = `🏆 Achievement! 🎇 The ${achievement}th Currency Thing! 🥳🎉`   // the description displayed on the achievement tooltip
    row.attr('data-achievement', desc)                  // adds the description as an attribute to be read in the CSS content property
}



// Old method here in case it becomes useless for something else
// kinda hacked method but simple and effective -> https://stackoverflow.com/questions/6135665/jquery-find-table-row-containing-table-cell-containing-specific-text
// $("tr:contains('143')").addClass('gold');
