# Utility functions for ID and hash generation
import hashlib
import sys
import platform

def get_env_id():
    info = f"{sys.executable}|{sys.version}|{platform.platform()}|{platform.python_implementation()}"
    return hashlib.sha256(info.encode()).hexdigest()

def get_private_id(env_id, public_ip, user_agent):
    info = f"{env_id}|{public_ip}|{user_agent}"
    return hashlib.sha256(info.encode()).hexdigest()
