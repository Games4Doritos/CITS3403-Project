from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import current_user, login_required


from app import db
from app.models import Profile, Account, Friendship
from app.forms import EditProfileForm, FriendCodeForm


user = Blueprint("user", __name__)

@user.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    mode = request.args.get('mode', 'view')
    friendCodeForm = FriendCodeForm()

    # Create edit profile form
    editForm = EditProfileForm()
    
    #query all the user's friends
    

    # Handle profile form submission
    if request.method == 'POST':

        if mode == 'edit':
            # Save profile form after validation
            if editForm.validate_on_submit():

                # Remove extra spaces from inputs
                username = editForm.username.data.strip()
                email = editForm.email.data.strip().lower()

                # Update account email
                current_user.email = email

                # New user without a profile yet
                if not current_user.profile:
                    profile = Profile(id=current_user.id,username=username)
                    db.session.add(profile)

                # Existing user updating username
                else:
                    current_user.profile.username = username

                db.session.commit()

                flash("Profile updated successfully.")
                return redirect(url_for("user.profile"))

            # Display validation errors
            else:
                for field, errors in editForm.errors.items():
                    for error in errors:
                        flash(error)
                return redirect(url_for("user.profile", mode="edit"))
        
        else:
            # Save friend code form after validation
            if friendCodeForm.validate_on_submit():
                
                friendCode = friendCodeForm.friendCode.data
                # Checks if a user with that code exists
                friendingAccount = Account.query.filter_by(friend_code=friendCode).first()
                
                
                if not friendingAccount:
                    flash("An account with that friend code doesn't exist!")
                    return redirect(url_for("user.profile"))
                
                # Checks if the friend code is their own
                if friendCodeForm.validate_friend_code(friendCode):
                    
                    friends = Friendship.query.filter(db.or_(Friendship.friendID1==current_user.id, Friendship.friendID2 == current_user.id)).all()
                    
                    #checks if the friendship already exists
                    alreadyExists = False
                    for i in friends:
                        if (i.friendID1 == current_user.id and i.friendID2 == friendingAccount.id) or (i.friendID1 == friendingAccount.id and i.friendID2 == current_user.id):
                            alreadyExists = True
                            break
                    
                    if alreadyExists:
                        flash("Friend already exists!")
                        return redirect(url_for("user.profile"))
                    
                    # checks if you have the friend limit
                    if len(friends) == 10:
                        flash("You can't make any more friends! Remove one to make ")
                        return redirect(url_for("user.profile"))
                    
                    
                    newFriendship = Friendship(friendID1=current_user.id, friendID2=friendingAccount.id, pending=True)
                    db.session.add(newFriendship)
                    db.session.commit()
                    flash("Friend Request Sent.")
                else:
                    flash("You can't friend yourself!")
                
                return redirect(url_for("user.profile"))
        
            else:
                flash("Friend code invalid.")
                return redirect(url_for("user.profile"))

    friends = Friendship.query.filter(db.or_(Friendship.friendID1==current_user.id, Friendship.friendID2 == current_user.id)).all()
    friendAccounts = []
    for i in friends:
        if i.friendID1 == current_user.id:
            friendAccounts.append(Account.query.filter_by(id=i.friendID2).first())
        else:
            friendAccounts.append(Account.query.filter_by(id=i.friendID1).first())
    print(friendAccounts)
    
    # New logged-in users must create profile first
    if not current_user.profile and mode != 'edit':
        return redirect(url_for("user.profile", mode="edit"))

    return render_template('profile.html', mode=mode, friendCodeForm=friendCodeForm, editForm=editForm, friendAccounts=friendAccounts)
