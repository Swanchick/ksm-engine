from hashlib import sha256


class HashPassword:
    @staticmethod
    def hash_password(password: str) -> str:
        hashed_text = sha256(password.encode())
        return hashed_text.hexdigest()

    @staticmethod
    def check_password(password: str, hashed_password: str) -> bool:
        return HashPassword.hash_password(password) == hashed_password
