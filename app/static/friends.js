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

    info.style.display = "flex";

    const friendActionForm = document.getElementById('friendActionForm');
    friendActionForm.friendEmail.value = friends[curFriend].email;


}