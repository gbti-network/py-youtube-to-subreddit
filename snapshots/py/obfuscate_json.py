import re

# Define the sensitive keys
SENSITIVE_KEYS = ["apiKey", "api_key", "private_key", "privateKey", "password", "secret", "token", "authToken"]

def obfuscate_sensitive_data(data):
    """
    Obfuscates sensitive data in a JSON object by replacing all non-special
    characters in the values of specified keys with 'X'.

    Returns a new dictionary object with the obfuscated data.
    """
    special_chars = r'[^\w\s]'
    obfuscated_data = {}
    for key, value in data.items():
        if isinstance(value, dict):
            obfuscated_data[key] = obfuscate_sensitive_data(value)
        elif isinstance(value, str) and any(sensitive_key.lower() in key.lower() for sensitive_key in SENSITIVE_KEYS):
            obfuscated_data[key] = re.sub(r'[\w\s]', 'X', value)
        else:
            obfuscated_data[key] = value
    return obfuscated_data
