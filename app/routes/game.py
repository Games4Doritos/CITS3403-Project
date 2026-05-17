from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from json import loads
from app import db
from app.models import BestStats

game = Blueprint("game", __name__)

SABOTAGE_DEBUFF = 0.5
FRIEND_BONUS = 0.5

@game.route('/play', methods=["GET", "POST"])
@login_required
def play():
    def validateResults(requestData, hasBonus):
        # checks if any of the figures are negative (invalid)
        if requestData["totalJumps"] < 0:
            return False
        if requestData["newCurrency"] < 0:
            return False
        if requestData["finalTime"] < 0:
            return False
        if requestData["totalScore"] < 0:
            return False
        # checks if total score < time (invalid as score += 100*deltaTime (s) at each frame)
        if requestData["totalScore"] < requestData["finalTime"]:
            return False
        bonusCheck = 0
        if hasBonus:
            bonusCheck = 0.5
        # Checks if the score is possible within the given time
        
        # Total possible score (without friend bonus) before max multiplier: 100 * 20(1.5 + 1.6 + ... + 5.4) = 276000
        # Total possible score (with friend bonus) before max multiplier: 100 * 20(2.0 + 2.1 + ... + 5.9) = 316000
        # It takes 800 seconds (40 intervals of 20 seconds) to get to max multiplier (increments 0.1 each interval)
        
        intervalCount = int(requestData["finalTime"])//20
        maxPossibleScore = 0
        if intervalCount <= 40:
            for i in range(intervalCount):
                maxPossibleScore += 20 * (1.5 + 0.1*i + bonusCheck)
            maxPossibleScore += (requestData["finalTime"] - 20*intervalCount)*(1.5+0.1*intervalCount + bonusCheck)
            maxPossibleScore *= 100
        else:
            maxMultiplierTime = requestData["finalTime"] - 800
            if hasBonus:
                maxPossibleScore = 100*(6 * maxMultiplierTime + 3160)
            else:
                maxPossibleScore = 100*(5.5 * maxMultiplierTime + 2760)
        if maxPossibleScore < requestData["totalScore"]:
            return False
        return True
    
    if request.method == "POST":
        requestData = loads(request.data.decode())
        if current_user.is_authenticated:
            valid = validateResults(requestData, current_user.has_bonus)
            if not valid:
                return "Invalid Run Results", 400
            
            if current_user.has_bonus:
                current_user.has_bonus = False

            if not current_user.best_stats:
                bestStats = BestStats(
                    id=current_user.id, 
                    highscore=requestData["totalScore"],
                    longest_time=requestData["finalTime"],
                    jump_count=requestData["totalJumps"],
                    currency=requestData["newCurrency"],
                    total_games=1
                )
                db.session.add(bestStats)
                db.session.commit()
            else:
                curBestStats = current_user.best_stats
                current_user.best_stats.total_games += 1

                if curBestStats.highscore < requestData["totalScore"]:
                    current_user.best_stats.highscore = round(requestData["totalScore"])
                if curBestStats.longest_time < requestData["finalTime"]:
                    current_user.best_stats.longest_time = requestData["finalTime"]
                current_user.best_stats.currency += int(requestData["newCurrency"])
                current_user.best_stats.jump_count += int(requestData["totalJumps"])
                
                # Deactivate debuff after run ends
                current_user.best_stats.debuffed = False
                db.session.commit()

            return "Run Successfully Submitted!", 200
    
    # Inject debuff into template for Jinja
    debuff = 0
    friendBonus = 0
    if current_user.is_authenticated and current_user.best_stats:
        if current_user.best_stats.debuffed:
            debuff = SABOTAGE_DEBUFF
    if current_user.is_authenticated and current_user.has_bonus:
        friendBonus = FRIEND_BONUS

    return render_template('play.html', debuff=debuff, friendBonus = friendBonus)