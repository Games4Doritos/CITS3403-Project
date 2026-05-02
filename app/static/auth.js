/*
  auth.js
  Handles:
  - Login / Sign Up form toggle
  - Title and subtitle text content switching
  - Tab highlight and underline animation
  - Default form display based on URL parameter (?mode=signup)
*/

// "DOMContentLoaded" makes sure html is fully loaded before js runs
document.addEventListener("DOMContentLoaded", function(){
    const authTitle = document.getElementById("auth_title");
    const authSubtilte = document.getElementById("auth_subtitle");

    const loginBtn = document.getElementById("login_btn");
    const signupBtn = document.getElementById("signup_btn");

    const loginForm = document.getElementById("login_form");
    const signupForm = document.getElementById("signup_form");

    const underline = document.getElementById("tab-underline");

    // login form displaying style
    function displayLogin(){
        // form title and subtitle
        authTitle.textContent = "Welcome Back";
        authSubtilte.textContent = "Continue your game and view your scores";

        // button styling
        loginBtn.className = "block w-1/2 py-2 text-center font-semibold text-white";
        signupBtn.className = "block w-1/2 py-2 text-center text-gray-500";

        // sliding bar position
        underline.style.left = "0";

        // displaying login form
        // hiding sign up form
        loginForm.style.display = "block";
        signupForm.style.display = "none";
    }

    // sign up form displaying style
    function displaySignup(){
        // form title and subtitle
        authTitle.textContent = "Create Your Account";
        authSubtilte.textContent = "Save your scores and compete on the leaderboard";

        // button styling
        signupBtn.className = "block w-1/2 py-2 text-center font-semibold text-white";
        loginBtn.className = "block w-1/2 py-2 text-center text-gray-500";

        // sliding bar position
        underline.style.left = "50%";

        //displaying signup form
        //hiding login form
        loginForm.style.display = "none";
        signupForm.style.display = "block";
    }

    // event listener for form buttons
    loginBtn.addEventListener("click", displayLogin);
    signupBtn.addEventListener("click", displaySignup);

    // check URL param
    // "mode" parameter defined here in case of need sign up form to be displayed first
    // login form is displayed by default
    const params = new URLSearchParams(window.location.search);
    const mode = params.get("mode");

    if (mode === "signup") {
        displaySignup();
    } else {
        displayLogin(); //default
    }

});

