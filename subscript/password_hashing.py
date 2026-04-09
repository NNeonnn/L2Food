from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password);

def verify_password(stored_hash: str, password: str) -> bool:
    try:
        ph.verify(stored_hash, password)
        return True
    except VerifyMismatchError:
        return False
    
# while (True):
#     psw = input()
#     hsh = hash_password(psw)
#     print("Password:", psw, "Hash:", hsh)
#     n = int(input())
#     for i in range(n):
#         tr = input()
#         if (verify_password(hsh, tr)):
#             print("Correct!")
#         else:
#             print("Wrong!")
