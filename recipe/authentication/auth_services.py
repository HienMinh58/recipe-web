from werkzeug.security import generate_password_hash, check_password_hash

from recipe.adapters.memory_repo import MemoryRepository
from recipe.domainmodel.user import User

class NameNotUniqueException(Exception):
    pass


class UnknownUserException(Exception):
    pass


class AuthenticationException(Exception):
    pass


def add_user(user_name: str, password: str, repo: MemoryRepository):
    user = repo.get_user(user_name)
    if user is not None:
        raise NameNotUniqueException

    password_hash = generate_password_hash(password)

    user = User(user_name, password_hash)
    repo.add_user(user)


def get_user(user_name: str, repo: MemoryRepository):
    user = repo.get_user(user_name)
    if user is None:
        raise UnknownUserException

    return user_to_dict(user)


def authenticate_user(user_name: str, password: str, repo:MemoryRepository):
    authenticated = False

    user = repo.get_user(user_name)
    if user is not None:
        authenticated = check_password_hash(user.password, password)
    if not authenticated:
        raise AuthenticationException


def user_to_dict(user: User):
    user_dict = {
        'user_name': user.username,
    }
    return user_dict
