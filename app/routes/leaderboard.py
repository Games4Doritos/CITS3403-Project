from flask import Blueprint, render_template, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import BestStats

leaderboard = Blueprint("leaderboard", __name__)

SABOTAGE_COST = 100
SABOTAGE_DEBUFF = 0.5

@leaderboard.route('/leaderboard')
def global_rank():
    # Get top 10 scores ordered by highscore (highest first)
    top_scores = BestStats.query.order_by(BestStats.highscore.desc()).limit(10).all()
    
    # Inject debuff value for current user
    debuff = 0
    if current_user.is_authenticated and current_user.best_stats:
        if current_user.best_stats.debuffed:
            debuff = SABOTAGE_DEBUFF

    return render_template('leaderboard.html', top_scores=top_scores, debuff=debuff)

@leaderboard.route('/sabotage/<int:target_id>', methods=['POST'])
@login_required
def send_sabotage(target_id):
    # Can't sabotage yourself
    if target_id == current_user.id:
        return jsonify({'error': 'You cannot sabotage yourself!'}), 400

    # Check target exists and has stats
    target_stats = BestStats.query.get(target_id)
    if not target_stats:
        return jsonify({'error': 'Player not found'}), 404

    # Check sender has enough currency
    if not current_user.best_stats or current_user.best_stats.currency < SABOTAGE_COST:
        return jsonify({'error': 'Not enough gems! You need 100 gems to sabotage.'}), 400

    # Check if target already debuffed (no stacking)
    if target_stats.debuffed:
        return jsonify({'error': 'This player is already debuffed!'}), 400

    # Deduct gems from sender
    current_user.best_stats.currency -= SABOTAGE_COST

    # Apply debuff to target
    target_stats.debuffed = True
    db.session.commit()

    return jsonify({'message': f'Player sabotaged! They will have a -{SABOTAGE_DEBUFF}x multiplier debuff on their next run.'}), 200