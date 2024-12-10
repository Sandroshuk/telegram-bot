users_data = {}

def save_data(user_id, key, value):
    if user_id not in users_data:
        users_data[user_id] = {}
    users_data[user_id][key] = value

def get_data(user_id):
    return users_data.get(user_id, {})
