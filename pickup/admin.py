from django.contrib import admin

from pickup.models import Transaction, Item, Note

admin.site.register(Transaction)
admin.site.register(Item)
admin.site.register(Note)
