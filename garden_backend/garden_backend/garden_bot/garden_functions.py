from garden_backend.garden_backend.models import Garden
from django.contrib.auth import get_user_model

User = get_user_model()


def garden_is_exist(login):
    owner = User.objects.get(username=login)
    try:
        owner.garden_set.all()
        return True
    except Exception:
        return False


def gardens_meters(login):
    user = User.objects.get(username=login)
    owner = user.owner
    gardens = owner.garden_set.all()
    meters = {}
    for garden in gardens:
        last_meters = garden.monthmeters_set.last()
        meters[garden.garden_plot] = (last_meters.meters, last_meters.time)
        return meters
