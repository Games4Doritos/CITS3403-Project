from flask import Blueprint, render_template

leaderboard = Blueprint("leaderboard", __name__)


@leaderboard.route('/leaderboard')
def global_rank():
    from app.models import BestStats
    # Get top 10 scores ordered by highscore (highest first)
    top_scores = BestStats.query.order_by(BestStats.highscore.desc()).limit(10).all()
    return render_template('leaderboard.html', top_scores=top_scores)
