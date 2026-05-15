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

    const authTabs = document.getElementById("auth_tabs");
    const loginBtn = document.getElementById("login_btn");
    const signupBtn = document.getElementById("signup_btn");

    const loginForm = document.getElementById("login_form");
    const signupForm = document.getElementById("signup_form");
    const resendVerificationForm = document.getElementById("resend_verification_form");

    const underline = document.getElementById("tab-underline");

    function hideAllForms() {
        loginForm.style.display = "none";
        signupForm.style.display = "none";

        if (resendVerificationForm) {
            resendVerificationForm.style.display = "none";
        }
    }

    // login form displaying style
    function displayLogin(){
        // form title and subtitle
        authTitle.textContent = "Welcome Back";
        authSubtilte.textContent = "Continue your game and view your scores";

        // button styling
        loginBtn.className = "block w-1/2 py-2 text-center font-semibold text-purple-200";
        signupBtn.className = "block w-1/2 py-2 text-center text-purple-400 opacity-60";

        // sliding bar position
        underline.style.left = "0";

        // displaying login form
        // hiding other form
        hideAllForms();
        authTabs.style.display = "flex";
        loginForm.style.display = "block";
    }

    // sign up form displaying style
    function displaySignup(){
        // form title and subtitle
        authTitle.textContent = "Create Your Account";
        authSubtilte.textContent = "Save your scores and compete on the leaderboard";

        // button styling
        signupBtn.className = "block w-1/2 py-2 text-center font-semibold text-purple-200";
        loginBtn.className = "block w-1/2 py-2 text-center text-purple-400 opacity-60";

        // sliding bar position
        underline.style.left = "50%";

        //displaying signup form
        //hiding other form
        hideAllForms();
        authTabs.style.display = "flex";
        signupForm.style.display = "block";
    }

    // event listener for form buttons
    loginBtn.addEventListener("click", displayLogin);
    signupBtn.addEventListener("click", displaySignup);

    function displayResendVerification(){
        authTitle.textContent = "Please verify your email before log in";
        authSubtilte.textContent =
            "Please check your email and follow the verification link.";

        loginBtn.className =
            "block w-1/2 py-2 text-center text-purple-400 opacity-60";

        signupBtn.className =
            "block w-1/2 py-2 text-center text-purple-400 opacity-60";

        underline.style.display = "none";

        hideAllForms();
        authTabs.style.display = "none";

        if (resendVerificationForm) {
            resendVerificationForm.style.display = "block";
        }
    }
    
    // check URL param
    // "mode" parameter defined here in case of need sign up form to be displayed first
    // login form is displayed by default
    const params = new URLSearchParams(window.location.search);
    const mode = params.get("mode");

    if (initialMode === "signup" || mode === "signup") {
        displaySignup();
    } else if (mode ==="resend-verification"){
        displayResendVerification();
    } else {
        displayLogin(); //default
    }

});

