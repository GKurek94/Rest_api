from passlib.context import CryptContext

pwd_context = CryptContext(schemas=['bcrypt'], depracated='auto')


def hash(password: str):
    return pwd_context.hash(password)
