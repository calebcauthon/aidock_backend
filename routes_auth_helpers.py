from functools import wraps

def authenticate_user_with_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request, jsonify
        from functools import wraps
        from db.user_model import UserModel

        print("All headers:")
        for header, value in request.headers.items():
            print(f"{header}: {value}")
        login_token = request.headers.get('login_token')
        if not login_token:
            return jsonify({"error": "No login token provided"}), 401
        
        user = UserModel.get_user_by_login_token(login_token)
        if not user:
            return jsonify({"error": "Invalid login token"}), 401
        
        return func(user, *args, **kwargs)
    return wrapper
