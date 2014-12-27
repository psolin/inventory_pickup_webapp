# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pickup', '0002_auto_20141226_0646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='transaction_num',
            field=models.ForeignKey(to='pickup.Transaction'),
            preserve_default=True,
        ),
    ]
