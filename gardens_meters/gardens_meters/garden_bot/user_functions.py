from gardens_meters.gardens_meters.models import Owner
import secrets
import string
from django.contrib.auth import get_user_model

User = get_user_model()


def is_register(login):
    try:
        User.objects.get(username=login)
        return True
    except Exception:
        return False


def register(phone, chat_id):
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(6))
    User = get_user_model()
    User.objects.create_user(username=phone, password=password)
    user = User.objects.get(username=phone)
    owner = Owner(phone_number=phone, chat_id=chat_id)
    owner.user = user
    owner.save()
    return {'login': phone, 'password': password}


def find_user(username):
    try:
        user = User.objects.get(username=username)
        return user
    except:
        return False
