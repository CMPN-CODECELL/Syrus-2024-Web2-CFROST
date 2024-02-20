/*
Purpose: Responsible for the main game logic

Author Name: Md. Tanvir Islam

Command to execute: N/A  
*/
var myClient = "shree";
var tracker = [];
var idTracker = [];
var bigBoard = 0;
var smallBoard = 0;
var guesses = 0;
var myLevel = 0;
var levelDisplay = 1;
var ogLevel = 0;
$(document).ready(function() {
	loadMe()
})

/*
	Function: loadMe
	 Purpose: Fires up the game as soon as the homepage loads by sending an AJAX 
			  request, in the success step of ajax request call the function which
			  loads the game. 
*/

function loadMe() {
	// myLevel = document.getElementById("mybtn").innerHTML;
	// alert(myLevel);
	var queryParams = new URLSearchParams(window.location.search);
	// Check if a specific parameter exists and get its value
	myLevel = parseInt(queryParams.get('level'));
	ogLevel = myLevel;
	myLevel = 2*(myLevel-1);
	myLevel += 2;
	postObj = {
		username: myClient,
		level: myLevel
	}
	$.ajax({
		url: "/intro",
		type: "POST", 
		contentType: "application/json", // type of content being sent
		dataType: "json", // type of content being received
		data: JSON.stringify(postObj),
		success: function(data) {
					guesses = 0;
					bigBoard = data.board.length;
					smallBoard = data.board[0].length;
					//$("#title").html("Player Name: " + data.username);
					$("#level").html("Level: " + (data.level/2 + data.level%2));
					$("#tries").html("Guesses: ");
					var name = 0;
					for (var i = 0; i < data.board.length; i++) {
						a = "a".repeat(i + 1);
						$("#board").append("<tr id = " + a + "></tr>");
						for (var j = 0; j < data.board[i].length; j++) {
							$("#" + a).append("<td><div value = " + i + " name =" + j + " id =" + name + " class = 'tile'></div></td>");
							name++;
						}
					}
					click(data);
				}
	});
}
/*
	Function: click
	 Purpose: Event listener function which loops through all the div elements
			  and waits for a click to happen, the reason for the for loop 
			  is to identify the div by its id and call in the chosenBlock
			  function in its call back to send to the server
		  in: data
*/
function click(data) {
	var name = 0;
	for (var i = 0; i < data.board.length; i++) {
		for (var j = 0; j < data.board[i].length; j++) {
			// Selector is the element extracted using the name
			$("#" + name).click(function() {
				chosenBlock($("#" + this.id).attr("value"), $("#" + this.id).attr("name"), this.id);
			})
			name++; // incrementing name selector 
		}
	}
}
/*
	Function: chosenBlock
	 Purpose: The click event listener calls this function in its callback,
			  this function is responsible for sending an AJAX request to the
			  server telling it exactly which tile is being clicked
		  in: i, j, id
*/
function chosenBlock(i, j, id) {
	var obj = {};
	obj.bigBox = i;
	obj.smallerBox = j;
	obj.id = id;
	postObj = {
		username: myClient,
		choice: JSON.stringify(obj)
	}
	$.ajax({
		url: "/card",
		type: "POST",
		contentType: "application/json",
		dataType: "json",
		data: JSON.stringify(postObj),
		success: function(data) {
			// prevents from inputting values inside the tile once its already flipped
			if (!document.getElementById(data.id).hasChildNodes()) {
				activate(data.id, data.value);
				tracker.push(data.value);
				idTracker.push(data.id);
				guesses++;
				scan(guesses);
				currentGuesses = Math.round(guesses / 2);
				$("#tries").html("Guesses: " + currentGuesses);
				if (tracker.length > 1) {
					if (tracker[0] !== tracker[1]) {
						deactivate(data.id); // Deactivate the current selection
						deactivate(idTracker[0]); // Deactivate the one before as well
						tracker.pop(); // Empty out the arrays to be filled with new ones
						idTracker.pop(); // Empty the id tracking array as well
						tracker.pop();
						idTracker.pop();
						scan(guesses); // scan for guesses
					}
					if (tracker[0] === tracker[1]) {
						while (tracker.length !== 0) {
							tracker.pop();
						}
						while (idTracker.length !== 0) {
							idTracker.pop();
						}
					}
				}
			}
	},
	});
}
/*
	Function: activate
	 Purpose: Flips the tile when clicked and adds a value
		  in: id, value
*/
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

function activate(id, value) {
	$("#" + id).attr("class", "flipped");
	$("#" + id).append("<span>" + value + "</span>");
}
/*
	Function: deactivate
	 Purpose: When clicked removes a value by removing the span and changes the physical look of the tile
		  in: id
*/
function deactivate(id) {
	window.setTimeout(function() {
		$("#" + id).attr("class", "tile");
		$("#" + id).children().remove();
	}, 800);
}
/*
	Function: scan
	 Purpose: Scans all the blocks to check if all of the blocks have been flipped
		  in: guesses 
*/
function scan(guesses) {
	var number = 0;
	var count = 0;
	// Everytime the for loop starts count gets incremented
	for (var i = 0; i < bigBoard; i++) {
		for (var j = 0; j < smallBoard; j++) {
			if (document.getElementById(number).hasChildNodes()) {
				count++;
			}
			number++;
		}
	}
	if (count === bigBoard * smallBoard) {
		var nothing = "";
		fetch('http://127.0.0.1:5000/update_game_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    "stats":{
						"date": formatDate(new Date()), // Format date
						"guesses": guesses // Send elapsed time in milliseconds
                    },
					"game": "memory"
                })
            })
		alert("You made " + guesses / 2 + " guesses!");
		$("#board").empty(); // Selects the tag and empties all the children associated with the tag
		$("#board").append("<h2>Loading up A New Level!</h2>");
		window.setTimeout(function() {
			$("#board").empty();
			window.location.href = "http://127.0.0.1:5000/game/memory?level=" + (ogLevel+1);
		}, 1500)
	}
}
