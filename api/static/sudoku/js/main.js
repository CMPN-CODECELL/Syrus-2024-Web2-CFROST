$(document).ready(function() {
    var startTime; // Variable to store start time

    // Start the timer
    startTime = new Date().getTime();

    // Menu settings
    $('#menuToggle, .menu-close').on('click', function(){
        $('#menuToggle').toggleClass('active');
        $('body').toggleClass('body-push-toleft');
        $('#theMenu').toggleClass('menu-open');
    });

    // Function to format date to dd-mm-yyyy
    function formatDate(date) {
        var day = date.getDate();
        var month = date.getMonth() + 1; // January is 0!
        var year = date.getFullYear();

        // Add leading zero if day or month is less than 10
        if (day < 10) {
            day = '0' + day;
        }
        if (month < 10) {
            month = '0' + month;
        }

        return day + '-' + month + '-' + year;
    }

    // Solve Button
    // Fix bootstrap modal trigger event
    $("#btn-solve").click(function(event) {
        if (rowValidation() && colValidation() && blockValidation()) {
            console.log("Correct Solution");
            var endTime = new Date().getTime(); // Get end time
            var elapsedTime = endTime - startTime; // Calculate elapsed time

            // Make POST request with formatted date and elapsed time
            fetch('http://127.0.0.1:5000/update_game_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    "stats":{
                        "date": formatDate(new Date()), // Format date
                        "duration": elapsedTime // Send elapsed time in milliseconds
                    },
					"game": "sudoku"
                })
            })
        } else {
            // FAILED
            // Rewrites Modal Message
            $("#modal-id .modal-body p").html("You are close enough. Please try again.");
            console.log("Incorrect Solution");
        }
    });
});
