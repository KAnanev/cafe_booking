from datetime import datetime
from uuid import UUID

import pytest

from accounts.users.domain.user import User


def test_user_creation():
    user = User.create_user('test_user', 'hashed_password', 'test@test.ru')
    assert isinstance(user.id, UUID)
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)
    assert user.username == 'test_user'
    assert user.email == 'test@test.ru'
    assert user.is_active is True
    assert user.role == 'user'


def test_user_created_without_data():
    with pytest.raises(ValueError, match='Нужно указать почту или телефон.'):
        user = User.create_user('test_user', 'hashed_password')
