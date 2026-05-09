"""Fix BestStats foreign key to link to Account

Revision ID: 901c786db2a4
Revises: 581b22c3c894
Create Date: 2026-05-09 18:39:23.619006

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '901c786db2a4'
down_revision = '581b22c3c894'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('best_stats')
    op.create_table('best_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('highscore', sa.Integer(), nullable=True),
        sa.Column('longest_time', sa.Float(), nullable=True),
        sa.Column('jump_count', sa.Integer(), nullable=True),
        sa.Column('currency', sa.Integer(), nullable=True),
        sa.Column('total_games', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['account.id'], name='fk_beststats_account'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('best_stats')
    op.create_table('best_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('highscore', sa.Integer(), nullable=True),
        sa.Column('longest_time', sa.Float(), nullable=True),
        sa.Column('jump_count', sa.Integer(), nullable=True),
        sa.Column('currency', sa.Integer(), nullable=True),
        sa.Column('total_games', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['profile.id'], name='fk_beststats_profile'),
        sa.PrimaryKeyConstraint('id')
    )