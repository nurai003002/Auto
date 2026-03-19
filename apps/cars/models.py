from django.db import models


class Car(models.Model):
    marka = models.CharField(max_length=50, verbose_name='Марка')
    model = models.CharField(max_length=50, verbose_name='Модель')
    gos_munber = models.CharField(max_length=20, verbose_name='Гос номер')
    year = models.PositiveIntegerField(verbose_name='Год выпуска')
    note = models.TextField(blank=True, default='', verbose_name='Примечание')

    def __str__(self):
        return f'{self.marka} {self.model} ({self.gos_munber})'

    class Meta:
        verbose_name = 'Машина'
        verbose_name_plural = 'Машины'


class TypeOfFix(models.Model):
    name = models.CharField(max_length=100, verbose_name='Тип ремонта')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип ремонта'
        verbose_name_plural = 'Типы ремонта'


class Fix(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Машина')
    repair_type = models.CharField(max_length=100, verbose_name='Тип ремонта')
    date = models.DateField(verbose_name='Дата ремонта')
    next_date = models.DateField(null=True, blank=True, verbose_name='Следующий ремонт')
    description = models.TextField(blank=True, default='', verbose_name='Комментарий')

    def __str__(self):
        return f'{self.car} - {self.repair_type} ({self.date})'

    class Meta:
        verbose_name = 'Ремонт'
        verbose_name_plural = 'Ремонты'
