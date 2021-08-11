//// Highlight achievement milestones!
// Uses two methods: a FLAWLESS one with 100% accuracy, and a HACKY one as backup that just does a ctrl+F if the other method is not available
// Using:   Python to get the achievement data
//          JQuery to read the python data, and add the Achievement class to the matching table rows

var method = document.currentScript.getAttribute("data-method")             // Gets the method specified in the HTML file's script tag

var table = $(".table-container");                                          // getting the table
var row_count = $(".table-container tr").length -1;                         // getting amount of rows in table (minus 1 because it starts at 0)

// Getting the Achievement Milestone & Trade ID values from Python as an array : [ACHIEVEMENT, TRADE ID]
$.getJSON({
        url: "/get_achievements",                                           // the app.route from Flask that routes to the desired Python function
        success: function(data){
            data.forEach(item => highlight_achievement(item));              // Highlighting each achievement in the HTML data using this data
        }
    });

// Adds the Achievement CSS class to every milestone trade by checking their index in the HTML table and giving them a specific tooltip description!
function highlight_achievement(item) {
    achievement = item[0];
    trade_id    = item[1];

    row = find_row(trade_id, method)

    row.addClass('achievement')
    
    desc = `🏆 Achievement! 🎇 The ${achievement}th Currency Thing! 🥳🎉`      // the description displayed on the achievement tooltip
    row.attr('data-achievement', desc)                                          // adds the description as an attribute to be read in the CSS content property

    console.log(`Search type: ${method}`)
    console.log(`Searching for Trade ID #${trade_id}`)
    console.log(row)
}

// Finding the wanted row
function find_row(trade_id, search_type) {
    // FLAWLESS method - finds table row by table ID
    if (search_type == "flawless") {
        index = row_count - trade_id;                                           // since the table is in reverse, we must reverse the index too
        row = table.find('tr').eq(index);                                       // finds the row with matching corrected index
    }

    // HACKED method - just does a ctrl+F and returns the first match
    else {
        row = $(`tr:contains('${trade_id}')`)
    }
    
    return row
}