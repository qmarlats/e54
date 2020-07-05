# Generated by Django 3.0.1 on 2019-12-28 23:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeatherHistoricalData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='creation date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='update date')),
                ('datetime', models.DateTimeField(db_index=True, verbose_name='date and time')),
                ('cloud_cover', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, verbose_name='cloud cover')),
                ('humidity', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, verbose_name='humidity')),
                ('pressure', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='pressure')),
                ('uv_index', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='UV index')),
                ('visibility', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='visibility')),
                ('precipitation_intensity', models.DecimalField(blank=True, decimal_places=4, max_digits=6, null=True, verbose_name='precipitation intensity')),
                ('precipitation_probability', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, verbose_name='precipitation probability')),
                ('precipitation_type', models.CharField(blank=True, max_length=5, null=True, verbose_name='precipitation type')),
                ('apparent_temperature', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='apparent temperature')),
                ('dew_point', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='dew point')),
                ('temperature', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='temperature')),
                ('wind_bearing', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='wind bearing')),
                ('wind_gust', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='wind gust')),
                ('wind_speed', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='wind speed')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weather_historical_data', to='locations.Location')),
            ],
            options={
                'default_related_name': 'weather_historical_data',
            },
        ),
    ]
