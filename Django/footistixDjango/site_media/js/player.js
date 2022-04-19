// async function fetchTeamsJSON(){
//     playerAPIURL = 'http://localhost/JSTutorial/playersAPI.php'
//     const response = await fetch(playerAPIURL);
//     const jsonResponse = await response.json();
//     return jsonResponse.data;
// }

// fetchPlayersJSON().then(data =>  {
//     player = data.find(el => el.full_name === $("#playerName").html())
//     console.log(player)
// });
$( document ).ready(function(){
    playerName = document.getElementById('playerName').innerHTML
    
    playerURL = "https://soccer.sportmonks.com/api/v2.0/players/search/"+playerName+"?api_token={{api_token}}"
    
    playerAPIURL = 'http://127.0.0.1:8000/api'
    fetch(playerAPIURL)
        .then(response => response.json())
        .then(data => {
            player = data.data.find(el => el.full_name === $("#playerName").html())
            console.log(player)
            document.getElementById("full_name").innerHTML = player.full_name
            document.getElementById("height").innerHTML = player.height
            document.getElementById("weight").innerHTML = player.weight
            document.getElementById("age").innerHTML = player.age
            document.getElementById("nationality").innerHTML = player.nationality
            document.getElementById("position").innerHTML = player.position
            document.getElementById("goals_home").innerHTML = player.goals_home
            document.getElementById("goals_away").innerHTML = player.goals_away
            document.getElementById("team").innerHTML = player.club_team_id

        })
        
});


//Send ratings to db
function sendRating(){
    const Rating = {
      1: $('#crossingRange').val(), 
      2: '',
      3: '',
      4: $('#through_passRange').val(),
      5: $('#visionRange').val(),
      // 6: '',
      // 7: '',
      // 8: '',
      // 9: '',
      // 10: '',
      // 11: '',
      // 12: '', 
    }
    
    var timerText = jQuery.param($('#seconds').html())
    var playerID = jQuery.param($('#playerID').html())
    console.log(playerID)
    var ratingsText = jQuery.param(Rating);
    
    //console.log(ratingsText);
    $.ajax({
      type: "POST",
      url: "http://127.0.0.1:8000/send_rate/",
      dataType: "text",
      data: {
        "ratings": ratingsText,
        "player": playerID,
        "timer": timerText,
        "csrfmiddlewaretoken": "{{csrf_token}}",
      },
      success: function(data){
        console.log("OK!")
        window.location=window.location;
      },
      error: function(err) {
        console.log("Error oqupied");
        
      } 
    });
  }
