from functools import wraps
from flask import request, jsonify

def extract_keys(*required_keys):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.json
            if not data:
                return jsonify({'error': 'No JSON payload provided',
                                 'status': 1}), 400

            request_data = {}
            for key in required_keys:
                if key not in data:
                    return jsonify({'keyError': f'{key} is missing',
                                    'status': 1}), 400
                request_data[key] = data[key]
            return f(request_data, *args, **kwargs)
        return decorated_function
    return decorator