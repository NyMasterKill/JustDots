from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abc123_create_task_tables'
down_revision = 'd76793fbec58_auth'  # Укажите ID первой миграции после сохранения
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
        sa.Column('status', sa.Enum('Открытая', 'В процессе', 'Закрытая', name='taskstatus'), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_tasks_id'), table_name='tasks')
    op.drop_table('tasks')