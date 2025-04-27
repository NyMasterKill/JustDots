import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Импорты моделей
from src.database import Base
from src.reviews.models import Review
from src.roles.models import Role
from src.order_responses.models import OrderResponse
from src.categories.models import Category
from src.auth.models import User
from src.skills.models import Skill
from src.user_portfolio.models import UserSkill

# Настройка конфигурации
config = context.config
fileConfig(config.config_file_name)

# Подключение к базе данных
connectable = engine_from_config(
    config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool
)

# Выполнение миграций
with connectable.connect() as connection:
    context.configure(
        connection=connection, target_metadata=Base.metadata
    )

    with context.begin_transaction():
        context.run_migrations()
    