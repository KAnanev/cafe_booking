# tests/test_data.py

# === Тестовые константы ===
TEST_PHONE_1 = '+79991234567'
TEST_PHONE_2 = '+79992222222'
TEST_PHONE_3 = '+79991111111'
TEST_PHONE_4 = '+79990000000'
TEST_PHONE_5 = '+79997654321'

TEST_EMAIL_1 = 'test@example.com'
TEST_EMAIL_2 = 'other@example.com'
TEST_EMAIL_3 = 'new@example.com'
TEST_EMAIL_4 = 'existing@example.com'
TEST_EMAIL_5 = 'unknown@example.com'
TEST_EMAIL_6 = 'test1@example.com'
TEST_EMAIL_7 = 'test2@example.com'

USERNAME_1 = 'testuser1'
USERNAME_2 = 'testuser2'
USERNAME_3 = 'existinguser'
USERNAME_4 = 'user1'
USERNAME_5 = 'user2'
USERNAME_6 = 'differentuser'
USERNAME_7 = 'anotheruser'
USERNAME_8 = 'newuser'
USERNAME_9 = 'conflictinguser'

DEFAULT_PASSWORD = 'secret'
DEFAULT_HASH = 'fake_hash'
USER_TEST_LOCAL = 'user@test.com'
MANAGER_TEST_LOCAL = 'manager@test.com'
ADMIN_TEST_LOCAL = 'admin@test.com'
PASSWORD: str = 'superpassword'
USERS_ROUTE: str = '/users/'
PAYLOAD: dict[str, str] = {
    'username': USERNAME_1,
    'email': TEST_EMAIL_1,
    'password': PASSWORD,
}
