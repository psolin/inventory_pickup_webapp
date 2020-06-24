#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models, connection
from datetime import datetime


class Transaction(models.Model):

    transaction_num = models.IntegerField(primary_key=True)
    customer_name = models.CharField(max_length=255, blank=True)
    transaction_date = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True)
    est_pickup_date = models.DateField(blank=True, null=True)
    forfeit_date = models.DateField(blank=True, null=True)

    # The status of the transaction, based on the items or the forfeit boolean

    def status(self):
        if self.forfeit_date is not None:
            return 'Forfeited'
        else:
            results = Item.objects.filter(transaction_num=self.pk)
            if len(results) > 0:
                active = 0
                for item in results:
                    if item.picked_up_on is None:
                        active += 1
                if active > 0:
                    return 'Active'
                else:
                    return 'Completed'
            else:
                return 'No Items'

    def __str__(self):  # __unicode__ on Python 2
        return str(self.pk)

    def final_pickup_date(self):
        if self.status() == 'Completed':
            cursor = connection.cursor()

            # Return latest item pickup date
            final_pickup = Item.objects.filter(
                transaction_num=self.pk).order_by('-picked_up_on')[0]
            final_pickup = final_pickup.picked_up_on
            return final_pickup.strftime('%A, %b. %-d, %Y')

    def overdue(self):

        # Only if the transaction is active:

        if self.status() == 'Active' and self.est_pickup_date != None:

            # If the estimated pickup date is greater than today's date, then
            # it's overdue

            now = datetime.now()
            todays_date = now.strftime('%Y-%m-%d')
            if self.est_pickup_date.strftime('%Y-%m-%d') > todays_date:
                return False
            else:
                return True
        else:
            return False

    def pretty_phone(self):
        if len(self.phone) == 10:
            phone_string = '(' + self.phone[0:3] + ') ' \
                + self.phone[3:6] + '-' + self.phone[6:10]
            return phone_string
        else:
            return self.phone


# Create your models here.

class Item(models.Model):

    itemid = models.IntegerField(primary_key=True)
    transaction_num = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    desc = models.CharField(max_length=255)
    picked_up_on = models.DateField(blank=True, null=True)

    def status(self):
        results = \
            Transaction.objects.get(transaction_num=self.transaction_num.pk)
        if self.picked_up_on is not None:
            return 'Picked up %s' \
                % self.picked_up_on.strftime('%A, %b. %-d, %Y')
        elif results.forfeit_date is not None:
            return 'Forfeited'
        else:
            return 'In Inventory'

    class Meta:

        db_table = 'item'

    def __str__(self):  # __unicode__ on Python 2
        return str(self.desc)

    # Override date string with "Forfeited" if never picked up


class Note(models.Model):

    noteid = models.IntegerField(primary_key=True)
    transaction_num = models.ForeignKey('Transaction',
                                        db_column='transaction_num', on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    date = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:

        db_table = 'note'

    def __str__(self):  # __unicode__ on Python 2
        return str(self.noteid)
