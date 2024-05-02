from engine import Engine

engine = Engine()

message = {"say": "Hello World"}
encrypted_message = engine.encrypt_data(message)
print(encrypted_message)

data = {"data": encrypted_message}
decrypted_message = engine.decrypt_data(data)
print(decrypted_message)
