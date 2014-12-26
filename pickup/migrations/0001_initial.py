# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('itemid', models.IntegerField(serialize=False, primary_key=True)),
                ('desc', models.CharField(max_length=255)),
                ('picked_up_on', models.DateField(null=True, blank=True)),
            ],
            options={
                'db_table': 'item',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('noteid', models.IntegerField(serialize=False, primary_key=True)),
                ('content', models.CharField(max_length=255)),
                ('date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'note',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('transaction_num', models.IntegerField(serialize=False, primary_key=True)),
                ('customer_name', models.CharField(max_length=255, blank=True)),
                ('transaction_date', models.DateField(null=True, blank=True)),
                ('phone', models.CharField(max_length=255, blank=True)),
                ('est_pickup_date', models.DateField(null=True, blank=True)),
                ('forfeit_date', models.DateField(null=True, blank=True)),
            ],
            options={
                'db_table': 'transaction',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='note',
            name='transaction_num',
            field=models.ForeignKey(to='pickup.Transaction', db_column=b'transaction_num'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='note',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='transaction_num',
            field=models.ForeignKey(to='pickup.Transaction', db_column=b'transaction_num'),
            preserve_default=True,
        ),
    ]
