from django.contrib.auth.models import User
from django.db import models
from datetime import datetime


class Transaction(models.Model):
    transaction_num = models.IntegerField(primary_key=True)
    customer_name = models.CharField(max_length=255, blank=True)
    transaction_date = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True)
    est_pickup_date = models.DateField(blank=True, null=True)
    forfeit_date = models.DateField(blank=True, null=True)

    # Status is either Active, Forfeited, or Completed
    def status(self):
        # If there is any forefeit date at all for the transaction, it's over.
        if self.forfeit_date:
            return 'Forfeited'
        # Pull all items in a trasaction and determines active vs in progress
        results = Item.objects.filter(transaction_num=self.pk)
        if results.exists():
            all_none = all(item.picked_up_on is None for item in results)
            any_none = any(item.picked_up_on is None for item in results)
            any_not_none = any(item.picked_up_on is not None for item in results)

            if all_none:
                return 'Active'
            elif any_none and any_not_none:
                return 'In Progress'
            else:
                return 'Completed'
        return 'No Items'

    def __str__(self):
        return str(self.pk)

    # Fill in a final pickup date if it is Completed status
    def final_pickup_date(self):
        if self.status() == 'Completed':
            final_pickup = Item.objects.filter(transaction_num=self.pk).order_by('-picked_up_on').first()
            if final_pickup and final_pickup.picked_up_on:
                return final_pickup.picked_up_on.strftime('%A, %b. %-d, %Y')
        return None

    # A sub-state of Active status, checking to see if pickup is overdue
    def overdue(self):
        if self.status() == 'Active' and self.est_pickup_date:
            now = datetime.now().date()
            return self.est_pickup_date < now
        return False

    class Meta:
        db_table = 'transaction'


class Item(models.Model):
    itemid = models.IntegerField(primary_key=True)
    transaction_num = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    desc = models.CharField(max_length=255)
    picked_up_on = models.DateField(blank=True, null=True)

    # Item Status is either Picked Up, Forfeited, or In Inventory
    def status(self):
        transaction = Transaction.objects.get(pk=self.transaction_num.pk)
        if self.picked_up_on:
            return 'Picked Up'
        elif transaction.forfeit_date:
            return 'Forfeited'
        return 'In Inventory'

    def __str__(self):
        return str(self.desc)

    class Meta:
        db_table = 'item'


class Note(models.Model):
    note_id = models.IntegerField(primary_key=True)
    transaction_num = models.ForeignKey(Transaction, db_column='transaction_num', on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    date = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.note_id)

    class Meta:
        db_table = 'note'
