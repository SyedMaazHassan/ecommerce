# Generated by Django 3.0.6 on 2020-07-29 11:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('application', '0005_products'),
    ]

    operations = [
        migrations.CreateModel(
            name='product_reviews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_star', models.IntegerField()),
                ('review_msg', models.TextField()),
                ('date', models.DateField(default='2020-07-29')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application.products')),
            ],
        ),
    ]
