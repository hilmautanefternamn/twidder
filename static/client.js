
// -------- LOAD HOME/PROFILE VIEW ------------
// load welcome (default) or home view (if token exist)
window.onload = function() {

  if( localStorage.getItem("token") != null) {
    document.getElementById('content').innerHTML = document.getElementById('profileview').innerHTML;
    // load home and profile view
    loadProfile(0);
  }
  else {
    document.getElementById('content').innerHTML = document.getElementById('welcomeview').innerHTML;
  }
}
// ----------- SIGN UP FUNCTION -------------
// get input signup-info from form and send/save in server
function signUp(form) {

  var user =
  {"email" : form.email.value,
  "password" : form.password[1].value,
  "firstname" : form.firstname.value,
  "familyname" : form.familyname.value,
  "gender" : form.gender.value,
  "city" : form.city.value,
  "country" : form.country.value};

  var result = serverstub.signUp(user);

  // status message
  document.getElementById('message').innerHTML = "<h2>" + result.message + "</h2>";
}
// ----------- SIGN IN FUNCTION -------------
// get input login-info from form and send to validate in server
function signIn(form) {

  var result = serverstub.signIn(form.email.value, form.password.value);

  // status message
  document.getElementById('message').innerHTML = "<h2>" + result.message + "</h2>";

  if(result.success) {
    localStorage.setItem("token", result.data);
    window.onload();
  }
}
// -------------- LOG OUT FUNCTION ---------------
// send token to be removed by server
function logOut() {

  var token = localStorage.getItem("token");
  var result = serverstub.signOut(token);

  if(result.success) {
      localStorage.removeItem("token");
      window.onload();
  }
  // status message
  document.getElementById('message').innerHTML = "<h2>" + result.message + "</h2>";
}
// ----------- LOAD PROFILE FUNCTION -------------
// use token to get profile info for home/browse-view
// call loadWall()
function loadProfile(form) {

  var token = localStorage.getItem("token");
  var destination_div; //home or browse
  var email = 0;
  var result;

  // home view (if we call loadProfile(0) from the onload function)
  if(form === 0) {
    result = serverstub.getUserDataByToken(token);
    destination_div = 'userinfo';
  }
  // browse view
  else {
    email = form.email.value;
    result = serverstub.getUserDataByEmail(token,email);
    destination_div = 'browseinfo';
      if(result.success) document.getElementById("browseprofile").style.display = "block";
  }
  // when a user is found on browse/or just logged in
  if(result.success) {
    document.getElementById(destination_div).innerHTML =
    "<p> First name: " + result.data.firstname + "</p>" +
    "<p> Family name: " + result.data.familyname + "</p>" +
    "<p> Gender: " + result.data.gender + "</p>" +
    "<p> City: " + result.data.city + "</p>" +
    "<p> Country: " + result.data.country + "</p>" +
    "<p> Email: " + result.data.email + "</p>";
    loadWall(email);
  }
  // status message
  document.getElementById('message').innerHTML = "<h2>" + result.message + "</h2>";
}
// ----------- LOAD WALL FUNCTION -------------
// load message wall from user on browse or home view
// email is the email of the destination user
function loadWall(email) {

  var token = localStorage.getItem("token");
  var to_email;
  var data;
  var destination_div; // browse or home

  // if function is called from home view, email = 0
  // this gives to_email = from_email in server
  if(email === 0) {
    destination_div = "wall";
    to_email = serverstub.getUserDataByToken(token).data.email;
    data = serverstub.getUserMessagesByToken(token);
  }
  else {
    destination_div = "browsewall";
    to_email = document.getElementById("toEmail").value;
    data = serverstub.getUserMessagesByEmail(token, to_email);
  }

  // only display wall when there are messages posted there
  if(data.data.length === 0) document.getElementById(destination_div).style.display = "none";
  else document.getElementById(destination_div).style.display = "block";

  // empty wall before reload/insertion
  document.getElementById(destination_div).innerHTML = "";

  // if messages found then display on wall
  if(data.success) {
    for(var i= 0; i < data.data.length; i++) {
        document.getElementById(destination_div).innerHTML +=
        "<p> To: " + to_email + "'s wall  From: " + data.data[i].writer + "</br>" + data.data[i].content + "</p>";
    }
  }
}
// ----------- COMPARE PASSWORDS FUNCTION -------------
// make sure repeated password match
// enable submit button when passwords match
function comparePasswords(i,j, button) {

  var passwords = document.getElementsByName("password");

  // no match
  if (passwords[i].value !== passwords[j].value) {
    document.getElementsByName("password")[j].style.color = "red";
  }
  // match
  else {
    document.getElementsByName("password")[j].style.color = "green";
    document.getElementsByName(button)[0].disabled = false;
  }
}
// ----------- CHANGE TAB FUNCTION -------------
// change tabs in header of home view, home, browse or account
function changeTab(id) {

document.getElementById(id+"content").style.display = "block";

  if (id === "home") {
    document.getElementById("browsecontent").style.display = "none";
    document.getElementById("accountcontent").style.display = "none";

    // empty email-field of browse view to get correct recipient of messages
    document.getElementById("toEmail").value = "";
  }
  else if(id === "browse") {
    document.getElementById("homecontent").style.display = "none";
    document.getElementById("accountcontent").style.display = "none";
  }
  else {
    document.getElementById("browsecontent").style.display = "none";
    document.getElementById("homecontent").style.display = "none";
  }
}
// ----------- CHANGE PASSWORD FUNCTION -------------
// make sure new and old password is not same and save new password in server
function changePassword(form) {

  var token = localStorage.getItem("token");
  var result = serverstub.changePassword(token, form.oldpassword.value, form.password[0].value);

  if(form.oldpassword.value === form.password[0].value) {
      document.getElementById('message').innerHTML =
      "<h2>Oh no! New password can't be same as old password</h2>";
  }
  // status message
  else{
      document.getElementById('message').innerHTML = "<h2>" + result.message + "</h2>";

  }

}
// ----------- POST MESSAGE FUNCTION -------------
// post message through server to browse or home wall
function postMessage(form) {

  var token = localStorage.getItem("token");

  // if called from home view, no recipient
  var to_email = document.getElementById("toEmail").value;
  if(to_email == "") to_email = null;

  // make sure message is not empty
  if( form.message.value == "") {
    document.getElementById('message').innerHTML = "<h2> Oh no! Can't post an empty message! </h2>";
  }
  else {

    var result = serverstub.postMessage(token, form.message.value , to_email);

    if(result.success) {
      // empty message field when message is successfully posted
      form.message.value = "";
      // reload wall
      loadWall(to_email);
    }
    // status message
    document.getElementById('message').innerHTML = "<h2>" + result.message + "</h2>";
  }
}
