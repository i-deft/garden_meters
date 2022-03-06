from django.db import models
from django.utils import timezone
from django.conf import settings

tz = timezone.get_default_timezone()


class Owner(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField('ФИО', max_length=100, blank=True)
    chat_id = models.CharField('ID телеграм чата',max_length=100, blank=True)
    phone_number = models.CharField('Номер телефона', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Собственник участка'
        verbose_name_plural = 'Собственники участков'

    def __str__(self):
        return self.user.username


class Garden(models.Model):
    owner = models.ForeignKey('Owner', on_delete=models.CASCADE, verbose_name='Собственник участка')
    garden_plot = models.PositiveIntegerField('Адрес участка', blank=True)
    is_data_entered_this_month = models.BooleanField('Показатели счетчиков уже переданы в этом месяце')
    is_paid_this_month = models.BooleanField('Оплата уже произведена в данном месяце')

    class Meta:
        verbose_name = 'Данные по участку'
        verbose_name_plural = 'Данные по участкам'

    def __str__(self):
        return f'Номер участка - {self.garden_plot}'


class MonthMeters(models.Model):
    title = models.ForeignKey('Garden', on_delete=models.CASCADE, verbose_name='Участок в собственности')
    meters = models.PositiveIntegerField('Показания счетчиков')
    time = models.DateTimeField()

    class Meta:
        verbose_name = 'Данные по ежемесячным показателям'
        verbose_name_plural = 'Данные по ежемесячным показателям'

    def __str__(self):
        return f'Показания за {self.time.astimezone(tz).strftime("%m.%Y")}'


class PhotoOfPay(models.Model):
    title = models.ForeignKey('Garden', on_delete=models.CASCADE, verbose_name='Участок в собственности')
    photo = models.FileField('Фотография счетчика', upload_to='photos/%Y/%m/%d/', blank=True)

    class Meta:
        verbose_name = 'Фото оплаты'
        verbose_name_plural = 'Фото оплаты'


