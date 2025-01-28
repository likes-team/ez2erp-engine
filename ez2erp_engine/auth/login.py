from ez2erp_engine import db
from ez2erp_engine.models import User


def user_login(email, password):
    print(type(User))
    user = User.ez2.select({'email': 'rmontemayor0101@gmail.com'})

    if user:
        return True
    else:
        return False

