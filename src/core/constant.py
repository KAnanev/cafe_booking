# Роли пользователя
ROLE_USER = 0
ROLE_MANAGER = 1
ROLE_ADMIN = 2

# Телефон
PHONE_MAX_LENGTH = 20

# Описание
DESCRIPTION_MAX_LENGTH = 400
DESCRIPTION_MIN_LENGTH = 10

# Кафе
CAFE_NAME_MAX_LENGTH = 100
CAFE_NAME_MIN_LENGTH = 1
CAFE_ADDRESS_MAX_LENGTH = 200

# UUID в строковом виде
UUID_LENGTH = 36

# Столы
TABLE_DESCRIPTION_MAX_LENGTH = 256
TABLE_MIN_SEATS_NUMBER = 1
TABLE_MAX_SEATS_NUMBER = 12
# Максимальная длина названия проекта
NAME_MAX_LENGTH = 100

# Граница для проверок "больше чем 0"
GT_ZERO = 0

# Время жизни JWT в секундах
JWT_LIFETIME_SECONDS = 3600

# Минимальная длина пароля
MIN_PASSWORD_LENGTH = 3

AUTH_TAG = 'Аутентификация'
USERS_TAG = 'Пользователи'

__all__ = [
    'NAME_MAX_LENGTH',
    'GT_ZERO',
    'JWT_LIFETIME_SECONDS',
    'MIN_PASSWORD_LENGTH',
    'AUTH_TAG',
    'USERS_TAG',
]
