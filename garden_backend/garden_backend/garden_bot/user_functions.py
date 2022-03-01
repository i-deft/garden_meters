from garden_backend.garden_backend.models import Garden, Owner
import secrets
import string
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model

User = get_user_model()


def is_register(phone):
    try:
        User.objects.get(username=phone)
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
