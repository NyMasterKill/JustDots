"""Create tasks table

Revision ID: 6b8f2d3e4a5b
Revises: 8822d5d2ee23
Create Date: 2025-05-02 12:00:00
"""
from alembic import op
import sqlalchemy as sa
from app.tasks.models import TaskStatus

# revision identifiers, used by Alembic.
revision = '6b8f2d3e4a5b'
down_revision = '8822d5d2ee23'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('budget_min', sa.Float(), nullable=True),
        sa.Column('budget_max', sa.Float(), nullable=True),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('category', sa.Enum('Разработка', 'Дизайн', 'Программирование', 'Копирайтинг', 'Другое', name='taskcategory'), nullable=False),
        sa.Column('custom_category', sa.String(length=255), nullable=True),
        sa.Column('skill_level', sa.Enum('Базовый', 'Средний', 'Продвинутый', name='taskskilllevel'), nullable=False),
        sa.Column('status', sa.Enum('Открытая', 'В процессе', 'Закрытая', name='taskstatus'), nullable=False, server_default=TaskStatus.OPEN.value),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_tasks_id'), table_name='tasks')
    op.drop_table('tasks')
    op.execute('DROP TYPE taskcategory')
    op.execute('DROP TYPE taskskilllevel')
    op.execute('DROP TYPE taskstatus')