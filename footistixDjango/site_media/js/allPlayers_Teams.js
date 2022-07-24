var players = []
var teams = []
var suggestionsArr = []
    $( document ).ready(function() {
      url = 'http://127.0.0.1:8000/search'
    //   fetch(url)
    //   .then(response => response.json())
    //   .then(data => console.log(data.players))

    // });
      fetch(url)
        .then(response => response.json())
        .then(data => {
          data.players.forEach(element => suggestionsArr.push(element))
          data.teams.forEach(element => suggestionsArr.push(element))
          data.nationals_teams.forEach(element => suggestionsArr.push(element))
        });
       console.log(suggestionsArr)
    });
  
