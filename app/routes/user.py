from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import current_user, login_required
from datetime import datetime, timezone

from app import db
from app.models import Profile, Account, Friendship
from app.forms import EditProfileForm, FriendCodeForm, FriendActionForm


user = Blueprint("user", __name__)

@user.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    mode = request.args.get('mode', 'view')
    # Create friend code form
    friendCodeForm = FriendCodeForm()
    
    # Create friend action form
    friendActionForm = FriendActionForm()

    # Create edit profile form
    editForm = EditProfileForm()

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
            
            formType = request.form.get('action')
            if formType == "friendRequest":
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
                
            elif formType == "gift/accept":
                
                if friendActionForm.validate_on_submit():
                    friendEmail = friendActionForm.friendEmail.data
                    friend = Account.query.filter_by(email=friendEmail).first()
                    # this query finds the specific friendship between the two accounts
                    friendship = Friendship.query.filter(db.or_(db.and_(Friendship.friendID1 == current_user.id, Friendship.friendID2 == friend.id), 
                                                                db.and_(Friendship.friendID2 == current_user.id, Friendship.friendID1 == friend.id))).first()
                    # if pending, the accept action if assumed (can't be manipulated because server-side)
                    if friendship.pending:
                        if current_user.id == friendship.friendID2:
                            # successfully make the friendship accepted (not pending)
                            friendship.pending = False
                            db.session.commit()
                        
                            flash('Friend Request Accepted!')
                            return redirect(url_for("user.profile"))
                        else:
                            flash("You can't accept your own request!")
                            return redirect(url_for("user.profile"))
                    # if not pending, the gift bonus action is assumed
                    else:
                        bonusTimestamp = friend.bonus_timestamp
                        curTimestamp = datetime.now()
                        if (curTimestamp - bonusTimestamp).total_seconds() >= 86400:
                            if not friend.has_bonus:
                                friend.has_bonus = True
                                friend.bonus_timestamp = datetime.now()
                                
                                flash('Bonus Gifted!')
                                return redirect(url_for("user.profile"))
                            else:
                                flash("That friend hasn't used up their existing bonus!")
                                return redirect(url_for("user.profile"))
                        else:
                            flash("It hasn't been a day since that friend's last bonus!")
                            return redirect(url_for("user.profile"))
                
                else:
                    flash('Invalid request to accept friend/gift bonus.')
                    return redirect(url_for("user.profile"))
                
            elif formType == "remove/reject":
                if friendActionForm.validate_on_submit():
                    friendEmail = friendActionForm.friendEmail.data
                    friend = Account.query.filter_by(email=friendEmail).first()
                    # this query finds the specific friendship between the two accounts
                    friendship = Friendship.query.filter(db.or_(db.and_(Friendship.friendID1 == current_user.id, Friendship.friendID2 == friend.id), 
                                                                db.and_(Friendship.friendID2 == current_user.id, Friendship.friendID1 == friend.id))).first()
                    # if pending, the reject action is assumed
                    if friendship.pending:
                        if current_user.id == friendship.friendID2:
                            db.session.delete(friendship)
                            db.session.commit()
                            flash('Friend Request Rejected.')
                            return redirect(url_for("user.profile"))
                        else:
                            flash("You can't reject your own request!")
                            return redirect(url_for("user.profile"))
                    # if not pending, the remove friend action is assumed
                    else:
                        db.session.delete(friendship)
                        db.session.commit()
                        flash('Friend Removed.')
                        return redirect(url_for("user.profile"))
                else:
                    flash('Invalid request to remove/ friend.')
                    return redirect(url_for("user.profile"))
            else:
                flash('Invalid Action.')
                return redirect(url_for("user.profile"))
                
    # finds all friendships involving the user
    friends = Friendship.query.filter(db.or_(Friendship.friendID1==current_user.id, Friendship.friendID2 == current_user.id)).all()
    friendAccounts = []
    for i in friends:
        iAccount = None
        if i.pending:
            if i.friendID1 == current_user.id:
                # don't show a pending request that you sent
                continue
            else:
                iAccount = Account.query.filter_by(id=i.friendID1).first()
                friendAccounts.append({'email': iAccount.email, 'username':iAccount.profile.username, 'pending':True})
        else:
            if i.friendID1 == current_user.id:
                iAccount = Account.query.filter_by(id=i.friendID2).first()
            else:
                iAccount = Account.query.filter_by(id=i.friendID1).first()
            friendAccounts.append({'email': iAccount.email, 'username':iAccount.profile.username, 'pending':False})
            
    # New logged-in users must create profile first
    if not current_user.profile and mode != 'edit':
        return redirect(url_for("user.profile", mode="edit"))

    return render_template('profile.html', mode=mode, friendCodeForm=friendCodeForm, editForm=editForm, 
                           friendAccounts=friendAccounts, friendActionForm = friendActionForm)
