from flask import Blueprint, render_template, request
from flask_login import current_user
from json import loads

from app import db
from app.models import BestStats

game = Blueprint("game", __name__)

@game.route('/play', methods=["GET", "POST"])
def play():
    
    def validateResults(requestData):
        #checks if any of the figures are negative (invalid)
        if requestData["totalJumps"] < 0:
            return False
        
        if requestData["newCurrency"] < 0:
            return False
            
        if requestData["finalTime"] < 0:
            return False

        if requestData["totalScore"] < 0:
            return False
        
        #checks if total score < time (invalid as score += 100*deltaTime (s) at each frame)
        if requestData["totalScore"] < requestData["finalTime"]:
            return False
        #checks if the score is possible within the given time
        #total score before max multiplier: 100(20*1.5 + 20*1.6 +...+ 20*5.4) = 276000 (happens over 800 seconds)
        #includes baseMultiplier progression and assumes the player is holding jump for the entire time (hence start at 1.5)
        intervalCount = int(requestData["finalTime"])//20
        maxPossibleScore = 0
        if intervalCount <= 40:
            for i in range(intervalCount):
                maxPossibleScore += 20 * (1.5 + 0.1*i)
            maxPossibleScore += (requestData["finalTime"] - 20*intervalCount)*(1.5+0.1*intervalCount)
            maxPossibleScore *= 100
        else:
            maxMultiplierTime = requestData["finalTime"] - 800
            maxPossibleScore = 100*(5.5 * maxMultiplierTime + 2760)
        if maxPossibleScore < requestData["totalScore"]:
            return False

        return True
    
    if request.method == "POST":
        
        requestData = loads(request.data.decode())
        #checks that the user submitting the run is logged in
        if current_user.is_authenticated:
            #basic server-side validation for results
            valid = validateResults(requestData)
            if not valid:
                return "Invalid Run Results", 400
            if not current_user.best_stats:
                #creates a new BestStats object and links it to the user for future uploads
                bestStats = BestStats(id=current_user.id, 
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
                # Increase games played count for every submitted run
                current_user.best_stats.total_games += 1
                #one final validation for types
                if curBestStats.highscore < requestData["totalScore"]:
                    current_user.best_stats.highscore = round(requestData["totalScore"])
                    
                if curBestStats.longest_time < requestData["finalTime"]:
                    current_user.best_stats.longest_time = requestData["finalTime"]
                    
                current_user.best_stats.currency += int(requestData["newCurrency"])
                current_user.best_stats.jump_count += int(requestData["totalJumps"])
                db.session.commit()
                    
            
            return "Run Successfully Submitted!", 200
        
    
    return render_template('play.html')