import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gardens_meters.gardens_meters.settings')
django.setup()

from gardens_meters.gardens_meters.models import Garden, MonthMeters
from django.contrib.auth import get_user_model

User = get_user_model()


def garden_is_exist(login):
    user = User.objects.get(username=login)
    owner = user.owner
    try:
        gardens = owner.garden_set.all()
        return True if gardens else False
    except Exception:
        return False

def garden_plots(login):
    user = User.objects.get(username=login)
    owner = user.owner
    gardens = owner.garden_set.all()
    gardens_set = {}
    for garden in gardens:
        gardens_set[garden.id] = garden.garden_plot
    return gardens_set


def garden_preivous_meters(login, garden_id):
    user = User.objects.get(username=login)
    owner = user.owner
    garden = owner.garden_set.get(id=int(garden_id))
    meters = {}
    last_meters = garden.monthmeters_set.last()
    meters[garden.garden_plot] = (last_meters.meters, last_meters.time.strftime("%d.%m.%Y"))
    return meters


def register_garden(login, adress):
    user = User.objects.get(username=login)
    owner = user.owner
    try:
        garden = Garden(garden_plot=adress, is_data_entered_this_month=False, owner_id=user.id)
        garden.save()
        garden_id = garden.id
        meters = MonthMeters(meters=0, garden_id=garden.id)
        meters.save()
        garden.monthmeters_set.add(meters)
        owner.garden_set.add(garden)
        return adress, garden_id
    except Exception:
        return False

def delete_garden(id):
    id = int(id)
    garden = Garden.objects.get(id=id)
    garden.delete()

def enter_meters(garden_plot, current_meters):
    pass

