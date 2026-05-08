/*
  profile.js

  Handles:
  - Switching between profile view and edit profile form
  - Showing and hiding profile sections
  - Default page display based on URL mode
    (/profile or /profile?mode=edit)
*/

// Show the edit profile section
function showEditProfile() {

    // Hide the normal profile view
    document.getElementById("profile-view").classList.add("hidden");

    // Show the edit profile form
    document.getElementById("edit-profile-view").classList.remove("hidden");
}

// Show the normal profile section
function showProfile() {

    // Hide the edit profile form
    document.getElementById("edit-profile-view").classList.add("hidden");

    // Show the main profile view
    document.getElementById("profile-view").classList.remove("hidden");
}
// "DOMContentLoaded" makes sure HTML is fully loaded before JavaScript runs
// Run when the page fully loads
document.addEventListener("DOMContentLoaded", function () {

    // If the page is opened in edit mode
    // example: /profile?mode=edit
    if (initialProfileMode === "edit") {

        // Automatically show edit profile section
        showEditProfile();

    } else {

        // Otherwise show normal profile view
        showProfile();
    }
});