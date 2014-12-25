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
        if self.forfeit_date != None:
            return "Forfeited"
        else:
            cursor = connection.cursor()
            item_query = """SELECT itemid, picked_up_on FROM item WHERE transaction_num = %s""" % (self.transaction_num)
            cursor.execute(item_query)

            results = cursor.fetchall()

            if len(results) > 0:
                active = 0
                for item in results:
                    if item[1] == None:
                        active += 1
                if active > 0:
                    return "Active"
                else:
                    return "Completed"
            else:
                return "No Items"

    class Meta:
        db_table = 'transaction'

    def __str__(self):              # __unicode__ on Python 2
        return str(self.transaction_num)

    def final_pickup_date(self):
        if self.status() == "Completed":
            cursor = connection.cursor()

            # Return latest item pickup date
            final_pickup_query = """SELECT picked_up_on FROM 'item' WHERE 'item'.transaction_num = %s ORDER BY picked_up_on DESC""" % (self.transaction_num)
            cursor.execute(final_pickup_query)
            results = cursor.fetchall()
            return results[0][0].strftime('%A, %b. %-d, %Y')

    def overdue(self):
        # Only if the transaction is active:
        if (self.status() == "Active") and (self.est_pickup_date != None):
            # If the estimated pickup date is greater than today's date, then it's overdue
            now = datetime.now()
            todays_date = now.strftime("%Y-%m-%d")
            if self.est_pickup_date.strftime("%Y-%m-%d") > todays_date:
                return False
            else:
                return True
        else:
            return False


# Create your models here.
class Item(models.Model):
    itemid = models.IntegerField(primary_key=True)
    transaction_num = models.ForeignKey(Transaction, db_column='transaction_num', on_delete=models.CASCADE)
    desc = models.CharField(max_length=255)
    picked_up_on = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'item'

    def __str__(self):              # __unicode__ on Python 2
        return str(self.desc)

    # Override date string with "Forfeited" if never picked up
    def status(self):
        cursor = connection.cursor()
        forfeit_status_query = """SELECT 'transaction'.forfeit_date FROM 'transaction'  WHERE 'transaction'.transaction_num = %s""" % (self.transaction_num)
        cursor.execute(forfeit_status_query)

        results = cursor.fetchall()[0][0]

        if self.picked_up_on != None:
            return "Picked up %s" % (self.picked_up_on.strftime('%A, %b. %-d, %Y'))
        elif results != None:
            return "Forfeited"
        else:
            return "In Inventory"


class Note(models.Model):
    noteid = models.IntegerField(primary_key=True)
    transaction_num = models.ForeignKey('Transaction', db_column='transaction_num', on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    date = models.DateTimeField(blank=True, null=True)
    user  = models.ForeignKey(User)

    class Meta:
        db_table = 'note'

    def __str__(self):              # __unicode__ on Python 2
        return str(self.noteid)