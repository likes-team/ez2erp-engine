from base64 import b64encode
from Crypto.Cipher import AES
from ez2erp_engine.models import BaseModel


class User(BaseModel):
    table_name = 'auth_users'

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.email = kwargs.get('email')
        self.password = kwargs.get('password')
        self.fname = kwargs.get('fname')
        self.lname = kwargs.get('lname')

    def encrypt_password(self, password, encryption_key):
        """Encrypt using pycryptodome
        """
        password_bytes = password.encode(encoding="utf-8")
        cipher  = AES.new(encryption_key, AES.MODE_CFB)
        ct_bytes = cipher.encrypt(password_bytes)
        iv = b64encode(cipher.iv).decode('utf-8')
        ct = b64encode(ct_bytes).decode('utf-8')
        self.password_iv = iv
        self.password_ct = ct

    def decrypt_password(self):
        pass

    def save(self):
        return self.__class__.ez2.insert(self.__dict__)

    def to_json(self):
        return {
            'id': self.id,
            'email': self.email,
        }
