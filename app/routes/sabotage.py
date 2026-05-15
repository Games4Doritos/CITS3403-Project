from flask import Blueprint, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import Sabotage, BestStats

sabotage = Blueprint("sabotage", __name__)

SABOTAGE_COST = 100  # coins
SABOTAGE_DEBUFF = 0.5  # multiplier reduction

@sabotage.route('/sabotage/<int:target_id>', methods=['POST'])
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
        return jsonify({'error': 'Not enough coins! You need 100 coins to sabotage.'}), 400

    # Check if target already has an active sabotage (no stacking)
    existing = Sabotage.query.filter_by(target_id=target_id, active=True).first()
    if existing:
        return jsonify({'error': 'This player is already sabotaged!'}), 400

    # Deduct coins from sender
    current_user.best_stats.currency -= SABOTAGE_COST

    # Create sabotage
    new_sabotage = Sabotage(
        target_id=target_id,
        sender_id=current_user.id,
        multiplier_debuff=SABOTAGE_DEBUFF,
        active=True
    )
    db.session.add(new_sabotage)
    db.session.commit()

    return jsonify({'message': f'Player sabotaged! They will have a -{SABOTAGE_DEBUFF}x multiplier debuff on their next run.'}), 200


@sabotage.route('/sabotage/status', methods=['GET'])
@login_required
def get_sabotage_status():
    # Get active sabotage on current user
    active_sabotage = Sabotage.query.filter_by(
        target_id=current_user.id,
        active=True
    ).first()

    if active_sabotage:
        return jsonify({
            'sabotaged': True,
            'debuff': active_sabotage.multiplier_debuff
        }), 200
    
    return jsonify({'sabotaged': False, 'debuff': 0}), 200