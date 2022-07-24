

//this func change label innerHTML by its slider
function changeValue(slider) {
  var labelID = slider.id;
  labelID = labelID.slice(0, -5);
  var output = document.getElementById(labelID + "Label"); // sorry, this noob way but we can fix it any time

  output.innerHTML = slider.value;
}

//this is one-time called function
var startTimer = (function() {
    var executed = false;
    return function() {
        if (!executed) {
            executed = true;
            timer(); // calling timer() function only first time
        }
    };
})();



function timer() {
  var minutesLabel = document.getElementById("minutes");
  var secondsLabel = document.getElementById("seconds");
  var totalSeconds = 0;
  setInterval(setTime, 1000);

  function setTime() {
    ++totalSeconds;
    secondsLabel.innerHTML = pad(totalSeconds % 60);
    minutesLabel.innerHTML = pad(parseInt(totalSeconds / 60));
  }
}
  function pad(val) {
    var valString = val + "";
    if (valString.length < 2) {
      return "0" + valString;
    } else {
      return valString;
    }
  }
//Getting name from serch and log it
  $(document).ready(function(){
    $(".submitSearch").click(function(){
      var searchedPlayer = $(".playerTest").val();
      console.log(searchedPlayer);
    
  
    })
  });
  
  
  function btnEnable(){
    if($('#email').val()!=''){
      $('#btnSubmit').removeAttr('disabled');
  }else{
    $('#btnSubmit').prop('disabled', true);
  }
  }

  function changeName(){
    var searchedPlayerPre = $(".playerSearchField").val();
    if (searchedPlayerPre != ""){
      var cleanName = searchedPlayerPre.replace(/[^\w\s0-9a-z]/gi, '');
      const split = cleanName.split(" ");
      for (var i = 0; i < split.length; i++){
        split[i]= split[i].charAt(0).toUpperCase()+ split[i].slice(1);
      }
      const searchedPlayer = split.join(" ");
      document.getElementById("playerName").innerHTML = searchedPlayer;
      $(".playerSearchField").val("");


    }
  }

  function showLogin(){
    $(".loginHidden").addClass('active');
    $(".signUpHidden").removeClass('active');
    $(".playerArea").addClass('disabled');
  }

  function hideLogin(){
    $(".loginHidden").removeClass('active');
    $(".playerArea").removeClass('disabled');

  }
  function showSignUp(){
    $(".signUpHidden").addClass('active');
    $(".loginHidden").removeClass('active');
    $(".playerArea").addClass('disabled');

  }
  function hideSignUp(){
    $(".signUpHidden").removeClass('active');
    $(".playerArea").removeClass('disabled');
  }

  function checkPasswords(){
    var password = $(".passwordInput").val();
    var passwordRepeat = $(".passwordRepeatInput").val();
    if (password != passwordRepeat){
      alert("Passwords do not match");
    };

    }
    
    





$(document).ready(function(){
  $(".submitSearch").click(changeName);

  $('.playerSearchField').keypress(function(e){
        if(e.which == 13){
            $('.submitSearch').click();
        }
    });
  $(".loginBtn").click(showLogin);
  $(".close-btn").click(hideLogin);
  $(".signUpBtn").click(showSignUp);
  $(".close-btn").click(hideSignUp);
  // $(".initialiseSignUp").click(checkPasswords, sendEmail);

});
 

   