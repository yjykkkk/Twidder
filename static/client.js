const X = 5; //min password length
const gender_list = ["man", "woman", "don't know", "prefer not to say"]; //option for gender selection
var login_token = "" //store login token at client-side(Not use)
var location_city, location_country;

displayView = function (view) {
    // the code required to display a view

    var screen = document.getElementById("screen");

    screen.innerHTML = view.innerHTML;
};

window.onload = function () {
    //code that is executed as the page is loaded
    //you shall put your own custom code here
    //window.alert() is not allowed to be used in your implementation
    var profileview = document.getElementById("profileview");
    var welcomeview = document.getElementById("welcomeview");

    if (localStorage.token != "" && localStorage.token != undefined) {
        // console.log(localStorage.token);
        displayView(profileview);
        document.getElementById("home_tab").click();
    }//Ensure not to sign out when reloading after signed in
    else {
        displayView(welcomeview);
    }
};
//Connect socket between client and server
function socket_connection(token) {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws");
    // const ws = new WebSocket("wss://twidder-541ea97252c5.herokuapp.com/ws");

    ws.onopen = (event) => {
        ws.send(token);
        console.log("open Socket");
    };

    ws.addEventListener('message', (event) => {
        if (event.data == 'close connection') {
            console.log("close connection");
            signout();
        }

    });

}
//verify the password the user set
function signup_passwd_verify(password, password_re, wrong_feedback) {
    var screen = document.getElementById("screen");
    if (password == password_re) {
        return 1
    }
    else {
        wrong_feedback.textContent = "Passwords do NOT match!!"
        wrong_feedback.style.opacity = 1;
        displayView(screen);
        return 0;
    }
}

//handle the signup function
function signup(event) {
    event.preventDefault(); //Prevent form from automatically submitting and page refresh
    var wrong_feedback = document.getElementById("wrong_feedback");
    var screen = document.getElementById("screen");
    var Email = document.getElementById("SignUpEmail").value;
    var Password = document.getElementById("SignUpPassword").value;
    var Password_re = document.getElementById("SignUpPassword_Re").value;
    var First_name = document.getElementById("First_Name").value;
    var Family_name = document.getElementById("Family_Name").value;
    var Gender = gender_list[parseInt(document.getElementById("Gender").value)]
    var City = document.getElementById("City").value;
    var Country = document.getElementById("Country").value;
    var profileview = document.getElementById("profileview");
    var signup_data = { email: Email, password: Password, firstname: First_name, familyname: Family_name, gender: Gender, city: City, country: Country };
    var result;
    if (signup_passwd_verify(Password, Password_re, wrong_feedback)) {
        var signup_req = new XMLHttpRequest();
        signup_req.open("POST", "/sign_up", true); //the third variable indicates async
        signup_req.setRequestHeader("Content-type", "application/json;charset=UTF-8");
        signup_req.send(JSON.stringify(signup_data));
        signup_req.onreadystatechange = function () {
            if (signup_req.readyState == 4) {
                if (signup_req.status == 201) {
                    var response = JSON.parse(signup_req.responseText);
                    wrong_feedback.textContent = null;
                    wrong_feedback.style.opacity = 0;
                    signin_process(Email, Password)
                }
                else if (signup_req.status == 400) {
                    var res = JSON.parse(signup_req.responseText)
                    wrong_feedback.textContent = "Wrong data format! " + res.message
                    wrong_feedback.style.opacity = 1;
                    displayView(screen);
                }
                else if (signup_req.status == 409) {
                    wrong_feedback.textContent = "The username is already taken! Please try another one!"
                    wrong_feedback.style.opacity = 1;
                    displayView(screen);
                }
                else {
                    console.log('Error:', signup_req.responseText);
                    var res = JSON.parse(signup_req.responseText)
                    wrong_feedback.textContent = res.message
                    wrong_feedback.style.opacity = 1;
                    displayView(screen);
                }
            }
        }
    }
    else {
        wrong_feedback.textContent = "Password do not match.";
        wrong_feedback.style.opacity = 1;
        displayView(screen);
    }
}

function signin(event) {
    event.preventDefault();
    var email = document.getElementById("SignInEmail").value;
    var password = document.getElementById("SignInPassword").value;
    signin_process(email, password);
}
//for better reuse signin function
function signin_process(email, password) {
    var wrong_feedback = document.getElementById("wrong_feedback");
    var screen = document.getElementById("screen");
    var profileview = document.getElementById("profileview");
    var signin_req = new XMLHttpRequest();
    signin_req.open("POST", "/sign_in", true);
    signin_req.setRequestHeader("Content-type", "application/json;charset=UTF-8");
    var signin_data = { "email": email, "password": password }
    signin_req.send(JSON.stringify(signin_data));
    signin_req.onreadystatechange = function () {
        if (signin_req.readyState == 4) {
            if (signin_req.status == 201) {
                var res = JSON.parse(signin_req.responseText)
                var login_token = res.data;
                localStorage.setItem("token", login_token);
                localStorage.setItem("email", email);
                displayView(profileview);
                document.getElementById("home_tab").click();
                socket_connection(login_token);
            }
            else if (signin_req.status == 404) {
                console.log("user not found")
                wrong_feedback.textContent = "The entered username does not exist! Please try again!"
                wrong_feedback.style.opacity = 1;
                displayView(screen);
            }
            else if (signin_req.status == 401) {
                console.log("incorrect password")
                wrong_feedback.textContent = "The entered password is not correct! Please try again!"
                wrong_feedback.style.opacity = 1;
                displayView(screen);
            }
            else {
                console.log("something went wrong")
                var res = JSON.parse(signin_req.responseText)
                wrong_feedback.textContent = res.message;
                wrong_feedback.style.opacity = 1;
                displayView(screen);
            }
        }
    }
}

//get User's data from the database by using GET method
function getUserData() {
    var info_email = document.getElementById("user_info_email");
    var info_firstname = document.getElementById("user_info_firstname");
    var info_familyname = document.getElementById("user_info_familyname");
    var info_gender = document.getElementById("user_info_gender");
    var info_city = document.getElementById("user_info_city");
    var info_country = document.getElementById("user_info_country");

    var token = localStorage.getItem("token");
    var req = new XMLHttpRequest();
    req.open("GET", "/get_user_data_by_token", true);
    req.setRequestHeader("Content-type", "application/json;charset=UTF-8");
    req.setRequestHeader("Authorization", "Bearer " + token);
    req.send()
    req.onreadystatechange = function () {
        if (req.readyState == 4) {
            if (req.status == 200) {
                var res = JSON.parse(req.responseText)
                let userdata2 = JSON.parse(req.responseText).data
                info_email.textContent = userdata2.email;
                info_firstname.textContent = userdata2.firstname;
                info_familyname.textContent = userdata2.familyname;
                info_gender.textContent = userdata2.gender;
                info_city.textContent = userdata2.city;
                info_country.textContent = userdata2.country;
            }
            else if (req.status == 401) {
                console.log("token is not correct");
            }
            else if (req.status == 500) {
                console.log("something went wrong")
            }
        }
    }
}

//handle clicking tab operation(click a tab and show the specific content)
function openTab(tabname, event) {
    var home_content = document.getElementById("home_content");
    var browse_content = document.getElementById("browse_content");
    var account_content = document.getElementById("account_content");

    var home_tab = document.getElementById("home_tab");
    var browse_tab = document.getElementById("browse_tab");
    var account_tab = document.getElementById("account_tab");

    //control tab's color after clicked
    home_tab.className = home_tab.className.replace(" active", "");
    browse_tab.className = browse_tab.className.replace(" active", "");
    account_tab.className = account_tab.className.replace(" active", "");
    event.currentTarget.className += " active";

    if (tabname == "Home") {
        home_content.style.display = "block";
        browse_content.style.display = "none";
        account_content.style.display = "none";
        getUserData();
        getMSG();
    }
    else if (tabname == "Browse") {
        home_content.style.display = "none";
        browse_content.style.display = "block";
        account_content.style.display = "none";
    }
    else if (tabname == "Account") {
        home_content.style.display = "none";
        browse_content.style.display = "none";
        account_content.style.display = "block";
    }
}

//implement the function of changing a user's password
function change_password(event) {
    event.preventDefault();
    var change_wrong_feedback = document.getElementById("change_wrong_feedback");
    var screen = document.getElementById("screen");
    var old_password = document.getElementById("change_old_passwd").value;
    var new_password = document.getElementById("change_new_passwd").value;
    var new_password_re = document.getElementById("change_new_passwd_re").value;
    var result;
    if (signup_passwd_verify(new_password, new_password_re, change_wrong_feedback)) {
        var req = new XMLHttpRequest();
        var token = localStorage.token;
        req.open("PUT", "/change_password", true);
        req.setRequestHeader("Content-type", "application/json;charset=UTF-8");
        req.setRequestHeader("Authorization", "Bearer " + token);
        var req_data = { "old_password": old_password, "new_password": new_password }
        req.send(JSON.stringify(req_data));
        req.onreadystatechange = function () {
            if (req.readyState == 4) {
                if (req.status == 201) {
                    var res = JSON.parse(req.responseText)
                    change_wrong_feedback.textContent = "password changed successfully!"
                    change_wrong_feedback.style.opacity = 1;
                    change_wrong_feedback.style.color = "green";
                    displayView(screen);
                }
                else if (req.status == 400) {
                    change_wrong_feedback.textContent = "new password must be at least " + X + " characters long"
                    change_wrong_feedback.style.opacity = 1;
                    change_wrong_feedback.style.color = "red";
                    displayView(screen);
                }
                else if (req.status == 401) {
                    change_wrong_feedback.textContent = "token is not correct"
                    change_wrong_feedback.style.opacity = 1;
                    change_wrong_feedback.style.color = "red";
                    displayView(screen);
                }
                else if (req.status == 409) {
                    change_wrong_feedback.textContent = "old password is not correct"
                    change_wrong_feedback.style.opacity = 1;
                    change_wrong_feedback.style.color = "red";
                    displayView(screen);
                }
            }
        }
    }
    else {
        change_wrong_feedback.textContent = "failed at password verify"
        change_wrong_feedback.style.opacity = 1;
        change_wrong_feedback.style.color = "red";
        displayView(screen);
    }
}

//handle signout function
function signout() {
    var welcomeview = document.getElementById("welcomeview");
    var req = new XMLHttpRequest();
    req.open("DELETE", "/sign_out", true);
    var token = localStorage.token;
    req.setRequestHeader("Content-type", "application/json;charset=UTF-8");
    req.setRequestHeader("Authorization", "Bearer " + token);
    req.send()
    req.onreadystatechange = function () {
        if (req.readyState == 4) {
            if (req.status == 200) {
                var res = JSON.parse(req.responseText)
                console.log('sign out succesfully')
                localStorage.removeItem("token");
                localStorage.removeItem("email");
                displayView(welcomeview);
            }
            else if (req.status == 401) {
                console.log("Token is not correct!")
            }
        }
    }
}

//get users' received messages data from database by using GET method
function getMSG() {
    var wall = document.getElementById("msg_wall");
    var wrong_msg = document.getElementById("wrong_msg")
    wall.innerHTML = "";
    var token = localStorage.token;
    var req = new XMLHttpRequest();
    req.open("GET", "/get_user_messages_by_token", true);
    req.setRequestHeader("Content-type", "application/json;charset=UTF-8");
    req.setRequestHeader("Authorization", "Bearer " + token);
    req.send()
    req.onreadystatechange = function () {
        if (req.readyState == 4) {
            if (req.status == 200) {
                var res = JSON.parse(req.responseText)
                for (let i = 0; i < res.data.length; i++) {
                    geocode(res.data[i].latitude, res.data[i].longitude).then(response => {
                        wall.innerHTML += "<div class='msg_list'>" + "<div class='msg_label'>from: " + res.data[i].writer + "</div>" + "<div draggable='true' ondragstart='drag(event)'>" + res.data[i].content + "</div></div>";
                        wall.innerHTML += "<div>" + response["city"] + "/" + response["country"] + "</div>";
                    })
                }
            }
            else if (req.status == 401) {
                wrong_msg.textContent = "token is not correct";
                wrong_msg.style.color = "red";
                wrong_msg.style.opacity = 1;
            }
            else {
                wrong_msg.textContent = "Get User Messages Failed";
                wrong_msg.style.color = "red";
                wrong_msg.style.opacity = 1;
            }
        }
    }
}

//add some messages to the specific user
function postMSG() {
    var msg = document.getElementById("home_tab_text").value;
    var wrong_msg = document.getElementById("wrong_msg");
    var token = localStorage.getItem("token");
    if (msg != "") {
        document.getElementById("home_tab_text").value = "";
        var req = new XMLHttpRequest();
        req.open("GET", "/get_user_data_by_token", true);
        req.setRequestHeader("Content-type", "application/json;charset=UTF-8");
        req.setRequestHeader("Authorization", "Bearer " + token);
        req.send()
        let userEmail;
        req.onreadystatechange = function () {

            if (req.readyState == 4) {
                if (req.status == 200) {
                    var res = JSON.parse(req.responseText)
                    let userdata = res.data;
                    userEmail = userdata.email
                    console.log('postmsg email ', userEmail);

                    var req2 = new XMLHttpRequest();
                    req2.open("POST", "/post_message", true);
                    req2.setRequestHeader("Content-type", "application/json;charset=UTF-8");
                    req2.setRequestHeader("Authorization", "Bearer " + token);
                    var longitude;
                    var latitude;
                    showPosition().then(res => {
                        res = JSON.parse(res);
                        latitude = res.latitude;
                        longitude = res.longitude;
                        console.log(latitude);
                        console.log(longitude);
                        var req2_data = { "email": userEmail, "message": msg, "latitude": latitude, "longitude": longitude };
                        req2.send(JSON.stringify(req2_data));
                        req2.onreadystatechange = function () {
                            if (req2.readyState == 4) {
                                if (req2.status == 201) {
                                    var res2 = JSON.parse(req2.responseText)
                                    wrong_msg.style.opacity = 1;
                                    wrong_msg.textContent = res2.message;
                                    wrong_msg.style.color = "green";
                                    getMSG();
                                }
                                else if (req2.status == 400) {//empty message
                                    wrong_msg.style.opacity = 1;
                                    wrong_msg.textContent = "Can not post empty Message!";
                                    wrong_msg.style.color = "red";
                                }
                                else if (req2.status == 401) {//incorrect token
                                    wrong_msg.style.opacity = 1;
                                    wrong_msg.textContent = "Token is not correct!";
                                    wrong_msg.style.color = "red";
                                }
                                else if (req2.status == 404) {//email not found
                                    wrong_msg.style.opacity = 1;
                                    wrong_msg.textContent = "The entered username does not exist!";
                                    wrong_msg.style.color = "red";
                                }
                                else if (req2.status == 500) {
                                    console.log("something went wrong")
                                }
                            }
                        }
                    })

                }
                else if (req.status == 401) {
                    console.log("token is not correct");
                }
                else if (req.status == 500) {
                    console.log("something went wrong")
                }
            }
        }

    }
    else {
        wrong_msg.style.opacity = 1;
        wrong_msg.textContent = "Can not post empty Message!";
        wrong_msg.style.color = "red";
    }
}

//get other users' received messages from database by using GET method
function getOtherMSG(event) {
    var other_email = document.getElementById("other_user_info_email").textContent;
    var other_msg_wall = document.getElementById("other_msg_wall");
    var browse_wrong_msg = document.getElementById("browse_wrong_msg");

    var req = new XMLHttpRequest();
    var token = localStorage.token;
    req.open("GET", "/get_user_messages_by_email/" + other_email, true);
    req.setRequestHeader("Content-type", "application/json;charset=UTF-8");
    req.setRequestHeader("Authorization", "Bearer " + token);
    var req_data = { "email": other_email }
    console.log("other email ", other_email)
    req.send(JSON.stringify(req_data));
    req.onreadystatechange = function () {
        if (req.readyState == 4) {
            if (req.status == 200) {
                var res = JSON.parse(req.responseText)
                let other_msg = res.data
                other_msg_wall.innerHTML = null;
                browse_wrong_msg.textContent = null;
                browse_wrong_msg.textContent = res.message
                browse_wrong_msg.style.color = "green";
                for (let i = 0; i < other_msg.length; i++) {
                    geocode(res.data[i].latitude, res.data[i].longitude).then(response => {
                        other_msg_wall.innerHTML += "<div class='msg_list'>" + "<div class='msg_label'>from: " + other_msg[i].writer + "</div>" + "<div draggable='true' ondragstart='drag(event)'>" + other_msg[i].content + "</div></div>";
                        other_msg_wall.innerHTML += "<div>" + response["city"] + "/" + response["country"] + "</div>";
                    })
                }

            }
            else if (req.status == 401) {
                browse_wrong_msg.textContent = "token is not correct"
                browse_wrong_msg.style.color = "red";
            }
            else if (req.status == 404) {
                browse_wrong_msg.textContent = "The entered username does not exist!"
                browse_wrong_msg.style.color = "red";
            }
            else {
                browse_wrong_msg.textContent = "something went wrong"
                browse_wrong_msg.style.color = "red";
            }
        }
    }
}

//get other users' data from the database by using GET method
function getOthersData(event) {
    event.preventDefault();
    var other_email = document.getElementById("browse_email").value;
    var screen = document.getElementById("screen");
    var browse_wrong_msg = document.getElementById("browse_wrong_msg");

    var other_info_email = document.getElementById("other_user_info_email");
    var other_info_firstname = document.getElementById("other_user_info_firstname");
    var other_info_familyname = document.getElementById("other_user_info_familyname");
    var other_info_gender = document.getElementById("other_user_info_gender");
    var other_info_city = document.getElementById("other_user_info_city");
    var other_info_country = document.getElementById("other_user_info_country");

    var req = new XMLHttpRequest();
    var token = localStorage.token;
    req.open("GET", "/get_user_data_by_email/" + other_email, true);
    req.setRequestHeader("Content-type", "application/json;charset=UTF-8");
    req.setRequestHeader("Authorization", "Bearer " + token);
    var req_data = { "email": other_email }
    req.send(JSON.stringify(req_data));
    req.onreadystatechange = function () {
        if (req.readyState == 4) {
            if (req.status == 200) {
                var res = JSON.parse(req.responseText)
                let userData = res.data
                other_info_email.textContent = userData.email
                other_info_firstname.textContent = userData.firstname
                other_info_familyname.textContent = userData.familyname
                other_info_gender.textContent = userData.gender
                other_info_city.textContent = userData.city
                other_info_country.textContent = userData.country
                browse_wrong_msg.textContent = "get info successfully"
                browse_wrong_msg.style.color = "green";
                getOtherMSG(event);
                displayView(screen);
            }
            else if (req.status == 404) {
                other_info_email.textContent = null
                other_info_firstname.textContent = null
                other_info_familyname.textContent = null
                other_info_gender.textContent = null
                other_info_city.textContent = null
                other_info_country.textContent = null
                browse_wrong_msg.textContent = "The entered username does not exist!"
                browse_wrong_msg.style.color = "red";
                getOtherMSG(event);
                displayView(screen);
            }
            else {
                other_info_email.textContent = null
                other_info_firstname.textContent = null
                other_info_familyname.textContent = null
                other_info_gender.textContent = null
                other_info_city.textContent = null
                other_info_country.textContent = null
                browse_wrong_msg.textContent = "something sent wrong"
                browse_wrong_msg.style.color = "red";
                getOtherMSG(event);
                displayView(screen);
            }
        }
    }
}

//add messages to others' messages wall
function postOtherMSG() {
    var other_email = document.getElementById("other_user_info_email").textContent;
    var other_msg = document.getElementById("browse_tab_text").value;
    var result;
    var browse_wrong_msg = document.getElementById("browse_wrong_msg");
    if (other_msg != "") {
        document.getElementById("browse_tab_text").value = "";
        var req = new XMLHttpRequest();
        req.open("POST", "/post_message", true);
        req.setRequestHeader("Content-type", "application/json;charset=UTF-8");
        var token = localStorage.getItem("token");
        req.setRequestHeader("Authorization", "Bearer " + token);
        var longitude;
        var latitude;
        showPosition().then(res => {
            res = JSON.parse(res);
            latitude = res.latitude;
            longitude = res.longitude;
            var req_data = { "email": other_email, "message": other_msg, "latitude": latitude, "longitude": longitude };
            req.send(JSON.stringify(req_data));
            req.onreadystatechange = function () {
                if (req.readyState == 4) {
                    if (req.status == 201) {
                        var res = JSON.parse(req.responseText)
                        browse_wrong_msg.textContent = res.message
                        browse_wrong_msg.style.color = "green";
                        getOtherMSG();
                    }
                    else if (req.status == 400) {
                        browse_wrong_msg.style.color = "red";
                        browse_wrong_msg.textContent = "Can not post empty Message!"
                    }
                    else if (req.status == 401) {
                        browse_wrong_msg.style.color = "red";
                        browse_wrong_msg.textContent = "token is not correct"
                    }
                    else if (req.status == 404) {
                        browse_wrong_msg.style.color = "red";
                        browse_wrong_msg.textContent = "The entered username does not exist!";
                    }
                    else {
                        browse_wrong_msg.style.color = "red";
                        browse_wrong_msg.textContent = "something went wrong"
                    }
                }
            }

        })
    }

}
//handle the function of dragging and dropping
function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("Text", ev.target.textContent);
}

function drop(ev) {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("Text");
    ev.target.value += data;
}

//using Promise to return the value from a callback function
function getGeolocation() {
    if (navigator.geolocation) {
        return new Promise((res, rej) => {
            navigator.geolocation.getCurrentPosition(res, rej);
        });
    }
    else {
        console.log("something wrong with geolocation");
    }

}

//Get latitude and longitude
async function showPosition() {
    var position = await getGeolocation();
    var geo_req = new XMLHttpRequest();
    var location = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
    }
    location = JSON.stringify(location)

    return location
}

// get geographical information from latitude and longitude
async function geocode(latitude, longitude) {
    var location = latitude + ", " + longitude;
    var API_key = "117922746245577873149x54572";
    var req_data = "/" + location + "?json=1&auth=" + API_key;
    var URL = "https://geocode.xyz" + req_data;
    const response = await fetch(URL);
    const data = await response.json();
    return data
}

//geocode API key: 454488463470380517071x101488