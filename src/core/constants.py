# =========================
# Роли пользователей
# =========================
ROLE_USER = 'User'
ROLE_MANAGER = 'Manager'
ROLE_ADMIN = 'Admin'


# =========================
# Аутентификация и безопасность
# =========================
SESSION_TTL_SECONDS = 3600
SESSION_TOUCH_THROTTLE_SECONDS = 60

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
PASSWORD_HASH_MIN_LENGTH = 60
PASSWORD_HASH_MAX_LENGTH = 255


# =========================
# Пользовательские данные
# =========================
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 50

EMAIL_MAX_LENGTH = 255

PHONE_MAX_LENGTH = 20
PHONE_PATTERN = r'^\+7\d{10}$'

TG_ID_MIN_LENGTH = 3
TG_ID_MAX_LENGTH = 64


# =========================
# Ограничения и проверки
# =========================
GT_ZERO = 0
CHECK_USER_EMAIL_OR_PHONE = 'ck_user_email_or_phone'

ADMIN_ONLY_USER_UPDATE_FIELDS = {'is_active', 'role'}


# =========================
# Описание / текстовые поля
# =========================
DESCRIPTION_MIN_LENGTH = 10
DESCRIPTION_MAX_LENGTH = 400


# =========================
# Кафе
# =========================
CAFE_NAME_MIN_LENGTH = 1
CAFE_NAME_MAX_LENGTH = 100
CAFE_ADDRESS_MAX_LENGTH = 200


# =========================
# Столы
# =========================
TABLE_MIN_SEATS_NUMBER = 1
TABLE_MAX_SEATS_NUMBER = 12
TABLE_DESCRIPTION_MAX_LENGTH = 256


# =========================
# Общие ограничения
# =========================
NAME_MAX_LENGTH = 100
UUID_LENGTH = 36


# =========================
# Медиа
# =========================
ALLOWED_IMAGE_CONTENT_TYPES = {
    'image/jpeg',
    'image/png',
}
MAX_IMAGE_SIZE = 5242880


# =========================
# OpenAPI / Swagger теги
# =========================
AUTH_TAG = 'Аутентификация'
USERS_TAG = 'Пользователи'

__all__ = [
    # roles
    'ROLE_USER',
    'ROLE_MANAGER',
    'ROLE_ADMIN',
    # auth & security
    'SESSION_TTL_SECONDS',
    'SESSION_TOUCH_THROTTLE_SECONDS',
    'PASSWORD_MIN_LENGTH',
    'PASSWORD_MAX_LENGTH',
    'PASSWORD_HASH_MIN_LENGTH',
    'PASSWORD_HASH_MAX_LENGTH',
    # user data
    'USERNAME_MIN_LENGTH',
    'USERNAME_MAX_LENGTH',
    'EMAIL_MAX_LENGTH',
    'PHONE_MAX_LENGTH',
    'PHONE_PATTERN',
    'TG_ID_MIN_LENGTH',
    'TG_ID_MAX_LENGTH',
    # checks
    'GT_ZERO',
    'CHECK_USER_EMAIL_OR_PHONE',
    'ADMIN_ONLY_USER_UPDATE_FIELDS',
    # descriptions
    'DESCRIPTION_MIN_LENGTH',
    'DESCRIPTION_MAX_LENGTH',
    # cafe
    'CAFE_NAME_MIN_LENGTH',
    'CAFE_NAME_MAX_LENGTH',
    'CAFE_ADDRESS_MAX_LENGTH',
    # tables
    'TABLE_MIN_SEATS_NUMBER',
    'TABLE_MAX_SEATS_NUMBER',
    'TABLE_DESCRIPTION_MAX_LENGTH',
    # common
    'NAME_MAX_LENGTH',
    'UUID_LENGTH',
    # openapi
    'AUTH_TAG',
    'USERS_TAG',
]
