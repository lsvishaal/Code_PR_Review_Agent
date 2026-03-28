"""Database utilities with security vulnerabilities for demo."""

import sqlite3


def query_user_by_id(user_id, db_path="db.sqlite3"):
    """Query user by ID - SQL injection vulnerability."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # SECURITY ISSUE: SQL injection vulnerability!
    # User input directly interpolated into query
    query = f"SELECT * FROM users WHERE id = {user_id}"
    
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    
    return result


def authenticate_user(username, password):
    """Authenticate user with hardcoded credentials."""
    # SECURITY ISSUE: Hardcoded credentials in code!
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "SuperSecret123!"
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return {"authenticated": True, "role": "admin"}
    
    return {"authenticated": False}


def store_api_key(api_key):
    """Store API key without encryption."""
    # SECURITY ISSUE: API key stored in plain text
    with open("/tmp/api_keys.txt", "a") as f:
        f.write(f"API_KEY={api_key}\n")
    
    return True


def fetch_data_from_external_api(url):
    """Fetch data from external API without validation."""
    import requests
    
    # SECURITY ISSUE: No URL validation - potential SSRF vulnerability
    # SECURITY ISSUE: No timeout - potential DoS
    response = requests.get(url)
    
    return response.json()
