"""测试密码验证"""
import hashlib
import secrets

# 测试密码验证
plain_password = 'mengxing2026'
hashed_password = 'c182051e5ee20e7d4f7bcd15234f42e6$e54047836ca305f778e59cb309bfd99367fa331ccb1bef3738190eb4f3d45394'

print(f'Plain password: {plain_password}')
print(f'Hashed password: {hashed_password}')
print(f"Contains '$': {'$' in hashed_password}")

salt, stored_hash = hashed_password.split('$', 1)
print(f'Salt: {salt}')
print(f'Stored hash: {stored_hash}')

computed_hash = hashlib.sha256((salt + plain_password).encode()).hexdigest()
print(f'Computed hash: {computed_hash}')
print(f'Match: {secrets.compare_digest(computed_hash, stored_hash)}')
