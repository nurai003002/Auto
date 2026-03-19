from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0001_initial'),
    ]

    operations = [
        # Add note to Car
        migrations.AddField(
            model_name='car',
            name='note',
            field=models.TextField(blank=True, default='', verbose_name='Примечание'),
        ),
        # Remove old Fix and recreate with new fields
        migrations.DeleteModel(
            name='Fix',
        ),
        migrations.CreateModel(
            name='Fix',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repair_type', models.CharField(max_length=100, verbose_name='Тип ремонта')),
                ('date', models.DateField(verbose_name='Дата ремонта')),
                ('next_date', models.DateField(blank=True, null=True, verbose_name='Следующий ремонт')),
                ('description', models.TextField(blank=True, default='', verbose_name='Комментарий')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cars.car', verbose_name='Машина')),
            ],
            options={
                'verbose_name': 'Ремонт',
                'verbose_name_plural': 'Ремонты',
            },
        ),
    ]
