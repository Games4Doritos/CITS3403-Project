console.log(friends);

let curFriend;

function selectFriend(email){
    let ind = 0;
    for (let i in friends){
        
        if (friends[i].email === email){
            break;
        }
        ind++;
    }
    curFriend = ind;
    const info = document.getElementById("friendInfo");
    if (friends[curFriend].username){
        info.children[0].textContent = friends[curFriend].username;
    } 
    else{
        info.children[0].textContent = friends[curFriend].email;
    }

    const friendActionForm = document.getElementById('friendActionForm');
    friendActionForm.friendEmail.value = friends[curFriend].email;

    if (friends[curFriend].pending){
        friendActionForm.children[2].children[0].textContent = "Accept Friend";
        friendActionForm.children[3].children[0].textContent = "Reject Friend";
    }
    else{
        friendActionForm.children[2].children[0].textContent = "Gift Bonus";
        friendActionForm.children[3].children[0].textContent = "Remove Friend";
    }

    info.style.display = "block";

    
    


}