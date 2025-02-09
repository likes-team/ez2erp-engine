import bcrypt
from ez2erp_engine.models import BaseModel


class User(BaseModel):
    table_name = 'auth_users'

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.email = kwargs.get('email')
        self.password = kwargs.get('password')
        self.fname = kwargs.get('fname')
        self.lname = kwargs.get('lname')
        self.password_hash = kwargs.get('password_hash')

    def encrypt_password(self, password):
        """Encrypt using bcrypt
        """
        password_bytes = password.encode(encoding="utf-8")
        self.salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, self.salt).decode('utf-8') 

    def decrypt_password(self, password):
        password_bytes = password.encode(encoding="utf-8")
        password_hash_bytes = self.password_hash.encode(encoding="utf-8")
        result = bcrypt.checkpw(password_bytes, password_hash_bytes)
        return result

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
        }
