fake_users_db = {
    "johndoe": {
        "id": 1,
        "login": "johndoe",
        "name": "John Doe",
        "company": "colab",
        "location": "NY",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "id": 2,
        "login": "alice",
        "name": "Alice Wonderson",
        "company": "colab",
        "location": "NY",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

def get_user_by_login(login):
    if login in fake_users_db:
        return fake_users_db[login]


def create_user(name, payload):
    fake_users_db[name] = payload
    return fake_users_db[name]
