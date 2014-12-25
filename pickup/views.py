from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from pickup.models import Transaction, Item, Note
from pickup.forms import AddTransactionForm
from django.db import connection
from django.contrib.auth.models import User
from django.utils import timezone
import time
import json
import datetime
from django.utils.timezone import localtime

############ Functions used to get info from the DB ############

# A count of the active transactions
def active_count(): 
    cursor = connection.cursor()
    active_count_query = """SELECT count(distinct "transaction".transaction_num) FROM "transaction" INNER JOIN "item" ON "transaction".transaction_num = "item".transaction_num WHERE ("transaction".forfeit_date IS NULL) AND picked_up_on IS NULL"""
    cursor.execute(active_count_query)

    results = cursor.fetchall()

    return results[0][0]

# Updating the transaction info pane
def transaction_info(transaction_number):
	pulled_transaction = Transaction.objects.get(transaction_num=transaction_number)
	return pulled_transaction.status(), pulled_transaction.final_pickup_date()


############ jQuery functions ############

# Used to add items to a transaction, refreshes page on submit.  In every view.
def add_form_view(request):
	form = AddTransactionForm(request.POST or None)

	if form.is_valid():
		save_it = form.save(commit=False)
		save_it.save()

		# Grab the transaction number and insert the items in the DB
		if request.method == 'POST':
			added_transaction = request.POST.get('transaction_num')
			transaction_lookup = Transaction.objects.get(transaction_num=added_transaction)
			items = request.POST.get('items')
			items = items.split(',')
			item_id_list = []
			for item in items:
				if item != "":
					add_item = Item(desc=item, transaction_num=transaction_lookup)
					add_item.save()

		# Redirect to active view -- broken!
		return render(request, 'pickup/active.html')

# Delete items and send back the item count
def trash_item(request):
	if request.GET.get('status') == "trash":
		trash_item = request.GET.get('item_id')
		Item.objects.filter(itemid=trash_item).delete()
		# (Eventually), itemid sent and the new count is returned.

		transaction_number = request.GET.get('transaction_number')

		pulled_transaction = Transaction(transaction_num=transaction_number)
		item_count = len(Item.objects.filter(transaction_num=pulled_transaction))

		# transaction_info(transaction_number) is an updated version of the status string

		return item_count, transaction_info(transaction_number)

# If we get a request to add items on the transaction page, add it to the DB.
def add_item(request):
	if request.GET.get('status') == "add_item":

		transaction_number = request.GET.get('transaction_number')
		item_lists = request.GET.get('item_list')

		new_item_ids = []

		def item_id_query():
			cursor = connection.cursor()
			item_id_query = """SELECT itemid FROM item ORDER BY itemid DESC"""
			cursor.execute(item_id_query)
			return cursor.fetchall()[0][0]

		# If a list, add each item.  If not, add the one item available.
		if "," in item_lists:
			item_lists = item_lists.split(",")
			for item in item_lists:
				pulled_transaction = Transaction(transaction_num=transaction_number)
				add_new_item = Item(transaction_num=pulled_transaction, desc=item)
				add_new_item.save()
				new_item_id = item_id_query()
				new_item_ids.append(new_item_id)

		else:
			pulled_transaction = Transaction(transaction_num=transaction_number)
			add_new_item = Item(transaction_num=pulled_transaction, desc=item_lists)
			add_new_item.save()
			new_item_id = item_id_query()
			new_item_ids.append(new_item_id)

		pulled_transaction = Transaction(transaction_num=transaction_number)
		item_count = len(Item.objects.filter(transaction_num=pulled_transaction))

		# Send back the generated itemid(s).
		# Remember, when an item is added, it changes the transaction to active automatically.
		return new_item_ids, item_count

def add_note(request):
	if request.GET.get('status') == "add_note":
		blurb = request.GET.get('blurb')
		user_id = request.GET.get('user_id')
		transaction_number = request.GET.get('transaction_number')
		now = datetime.datetime.now()
		pulled_transaction = Transaction(transaction_num=transaction_number)
		pulled_user = User(pk=user_id)
		new_note = Note(transaction_num=pulled_transaction, content=blurb, date=now, user=pulled_user)
		new_note.save()

		# The note that we just added ...
		latest_note = Note.objects.latest('noteid')

		# ... the id ...
		latest_note_date = localtime(latest_note.date)

		# ... the user's first name who added it ...
		note_user = User.objects.get(pk=user_id)
		note_user = note_user.first_name

		# ... and the new note count for the transaction.
		note_count = len(Note.objects.filter(transaction_num=pulled_transaction))

		return latest_note_date.strftime('%A, %b. %d, %Y, %I:%m %p'), note_count, note_user

# Edit individual items
def edit_item(request):
	if request.GET.get('status') == "edit_item":
		item_id = request.GET.get('current_item_id')
		new_desc = request.GET.get('new_desc')
		Item.objects.filter(itemid=item_id).update(desc=new_desc)
		# send new active count and all of that jazz

# Edit individual items
def edit_item_date(request):
	if request.GET.get('status') == "edit_item_date":
		item_id = request.GET.get('current_item_id')
		new_date = request.GET.get('new_date')
		transaction_number = request.GET.get('transaction_number')
		Item.objects.filter(itemid=item_id).update(picked_up_on=new_date)
		new_item_date = Item.objects.get(itemid=item_id)
		

		return new_item_date.status(), transaction_info(transaction_number)

# Editing a transaction's information
def edit_transaction(request):
	if request.GET.get('status') == "edit_transaction":
		transaction_number = request.GET.get('transaction_number')
		edited_transaction_number = request.GET.get('edited_transaction_number')
		transaction_date = request.GET.get('transaction_date')
		est_pickup_date = request.GET.get('est_pickup_date')
		customer_name = request.GET.get('customer_name')
		phone_number = request.GET.get('phone_number')

		returned_data = {'transaction_date': transaction_date, 'est_pickup_date': est_pickup_date, 'customer_name': customer_name, 'phone': phone_number}

		# If the transaction number needs to be changed, do this first
		if transaction_number != edited_transaction_number:
			Transaction.objects.filter(transaction_num=transaction_number).update(transaction_num=edited_transaction_number)

			# Cascading update does not work so um, run some queries?
			cursor = connection.cursor()
			update_items_query = "UPDATE 'item' SET transaction_num = %s WHERE transaction_num = %s" % (edited_transaction_number, transaction_number)
			cursor.execute(update_items_query)

			cursor = connection.cursor()
			update_notes_query = "UPDATE 'note' SET transaction_num = %s WHERE transaction_num = %s" % (edited_transaction_number, transaction_number)
			cursor.execute(update_notes_query)

			new_transaction_num = edited_transaction_number
		else:
			new_transaction_num = transaction_number

		for entry in returned_data:
			if returned_data[entry] != "":
				print returned_data[entry]
				if entry == "transaction_date":
					Transaction.objects.filter(transaction_num=new_transaction_num).update(transaction_date=returned_data[entry])
				elif entry == "est_pickup_date":
					Transaction.objects.filter(transaction_num=new_transaction_num).update(est_pickup_date=returned_data[entry])
				elif entry == "customer_name":
					Transaction.objects.filter(transaction_num=new_transaction_num).update(customer_name=returned_data[entry])
				elif entry == "phone":
					Transaction.objects.filter(transaction_num=new_transaction_num).update(phone=returned_data[entry])

		return new_transaction_num

# Forfeit or reinstate a transaction
def forfeit(request):
	if request.GET.get('status') == "forfeit":
		transaction_number = request.GET.get('transaction_number')
		pulled_transaction = Transaction.objects.get(transaction_num=transaction_number)
		
		# If the transaction is not forfeited, add today's date.  Otherwise, clear it.
		if pulled_transaction.forfeit_date == None:
			today = time.strftime('%Y-%m-%d')
			Transaction.objects.filter(transaction_num=transaction_number).update(forfeit_date=today)
		else:
			Transaction.objects.filter(transaction_num=transaction_number).update(forfeit_date=None)


def check_item(request):
	if request.GET.get('status') == "check_item":
		item_to_check = request.GET.get('current_id')

		transaction_number = request.GET.get('transaction_number')

		pulled_item = Item.objects.get(itemid=item_to_check)

		if pulled_item.picked_up_on == None:
			# If the item is not picked up (there is no date), update the date
			pickup_day = time.strftime('%Y-%m-%d')
			Item.objects.filter(itemid=item_to_check).update(picked_up_on=pickup_day)
		else:
			# Remove the date if there is actually a date there
			cursor = connection.cursor()
			cursor.execute("UPDATE 'item' SET picked_up_on = NULL WHERE itemid = %s", [int(item_to_check)])

		
		pulled_transaction = Transaction.objects.get(transaction_num=transaction_number)
		transaction_status = pulled_transaction.status()
		current_active = active_count()

		# Pull the item again in its new state
		pulled_item = Item.objects.get(itemid=item_to_check)
		item_status = pulled_item.status()
		item_date = pulled_item.picked_up_on

		if item_date != None:
			item_date = item_date.strftime('%A, %b. %d, %Y')
		else:
			item_date = ""

		return item_status, current_active, transaction_info(transaction_number), item_date

def remove_transaction(request):
	if request.GET.get('status') == "remove_transaction":
		transaction_number = request.GET.get('transaction_number')
		pulled_transaction = Transaction.objects.get(transaction_num=transaction_number)
		pulled_transaction.delete()



############ And now, the views ############


# Historical Inventory View
def history(request):
	
	# 404 if not logged in
	if not request.user.is_authenticated():
		return render(request, 'pickup/404.html')

	data = {}

	t = Transaction.objects.all().order_by('-transaction_date', '-transaction_num')
	
	# Sort to only show un-active items
	u = []
	for item in t:
		if item.status() != "Active":
			u.append(item)

	data['transaction_list'] = u

	add_form = add_form_view(request)
	data['add_form'] = add_form

	return render(request, 'pickup/history.html', data)

# Transaction View
def transaction(request, transaction=None):
	# 404 if not logged in
	if not request.user.is_authenticated():
		return render(request, 'pickup/404.html')

	data = {}

	edited_transaction = edit_transaction(request)
	if edited_transaction != None:
		return HttpResponse(json.dumps(edited_transaction), content_type="application/json")

	edited_date = edit_item_date(request)
	if edited_date != None:
		return HttpResponse(json.dumps(edited_date), content_type="application/json")

	item_count_response = trash_item(request)
	if item_count_response != None:
		return HttpResponse(json.dumps(item_count_response), content_type="application/json")

	note_data = add_note(request)
	if note_data != None:
		return HttpResponse(json.dumps(note_data), content_type="application/json")

	t = Transaction.objects.filter(transaction_num = transaction)
	data['transaction_list'] = t

	n = Note.objects.filter(transaction_num = transaction).order_by('-date')
	data['note_list'] = n

	add_form = add_form_view(request)
	data['add_form'] = add_form

	pk = add_item(request)
	if pk != None:
		return HttpResponse(json.dumps(pk), content_type="application/json")

	item_info = check_item(request)
	if item_info != None:
		return HttpResponse(json.dumps(item_info), content_type="application/json")

	edit_item(request)

	forfeit(request)

	remove_transaction(request)

	return render(request, 'pickup/transaction.html', data)

def active(request):
	# 404 if not logged in
	if not request.user.is_authenticated():
		return render(request, 'pickup/404.html')

	data = {}

	t = Transaction.objects.all().order_by('-transaction_date', '-transaction_num')
	i = Item.objects.all()
	

	active_item_list = []
	for item in i:
		if item.status() == "In Inventory":
			active_item_list.append(item)

	
	# Sort to only show active transactions
	u = []
	for transaction in t:
		if transaction.status() == "Active":
			u.append(transaction)

	data['item_list'] = active_item_list

	v = []
	for transaction in t:
		if transaction.overdue() == True:
			v.append(transaction)

	data['overdue_list'] = v

	data['transaction_list'] = u

	add_form = add_form_view(request)
	data['add_form'] = add_form

	return render(request, 'pickup/active.html', data)

def login(request):

	return render(request, 'pickup/login.html')

def home(request):
	# 404 if not logged in
	if not request.user.is_authenticated():
		return render(request, 'pickup/404.html')

	data = {}

	t = Transaction.objects.all().order_by('-transaction_date', '-transaction_num')

	overdue_list = []
	for transaction in t:
		if transaction.overdue() == True:
			overdue_list.append(transaction)

	data['overdue_transactions'] = len(overdue_list)

	add_form = add_form_view(request)
	data['add_form'] = add_form

	return render(request, 'pickup/home.html', data)

# 404 Template
def handler404(request):
    response = render_to_response('pickup/404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response