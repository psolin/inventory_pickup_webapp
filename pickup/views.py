import json
import logging
import time

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.timezone import localtime
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from pickup.models import Transaction, Item, Note
from .forms import TransactionForm, ItemForm, SignUpForm, EditProfileForm

logger = logging.getLogger(__name__)


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'pickup/profile_edit.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'pickup/signup.html', {'form': form})


def transaction_info(transaction_number):
    pulled_transaction = Transaction.objects.get(transaction_num=transaction_number)
    return (pulled_transaction.status(), pulled_transaction.final_pickup_date())


@login_required
def check_transaction_num(request):
    transaction_num = request.GET.get('transaction_num')
    exists = Transaction.objects.filter(transaction_num=transaction_num).exists()
    return JsonResponse({'exists': exists})


@csrf_protect
@login_required
@require_POST
def add_transaction(request):
    transaction_form = TransactionForm(request.POST)
    if transaction_form.is_valid():
        add_new_transaction = transaction_form.save()
        items = request.POST.get('items')

        if ',' in items:
            item_lists = items.split(',')
            for item in item_lists:
                add_new_item = ItemForm({'transaction_num': add_new_transaction.pk, 'desc': item})
                if add_new_item.is_valid():
                    add_new_item.save()
        else:
            add_new_item = ItemForm({'transaction_num': add_new_transaction.pk, 'desc': items})
            if add_new_item.is_valid():
                add_new_item.save()

        logger.info('%s added Transaction # %s', request.user, add_new_transaction.transaction_num)
        return JsonResponse({'redirect_url': reverse('active')})
    else:
        logger.warning('Invalid transaction form: %s', transaction_form.errors)
        return JsonResponse({'errors': transaction_form.errors}, status=400)


def trash_item(request):
    if request.POST.get('status') == 'trash':
        trashed_item = request.POST.get('item_id')
        item_name = Item.objects.get(pk=trashed_item)

        Item.objects.filter(itemid=trashed_item).delete()

        transaction_number = request.POST.get('transaction_number')
        pulled_transaction = Transaction.objects.get(transaction_num=transaction_number)
        item_count = Item.objects.filter(transaction_num=pulled_transaction).count()

        logger.info('%s trashed Item # %s (%s)', request.user, trashed_item, item_name)

        return item_count, transaction_info(transaction_number)


def add_item(request):
    if request.POST.get('status') == 'add_item':
        transaction_number = request.POST.get('transaction_number')
        item_lists = request.POST.get('item_list')

        new_item_ids = []

        def item_id_query():
            cursor = connection.cursor()
            cursor.execute("SELECT itemid FROM item ORDER BY itemid DESC")
            return cursor.fetchall()[0][0]

        if ',' in item_lists:
            item_lists = item_lists.split(',')
            for item in item_lists:
                pulled_transaction = Transaction.objects.get(transaction_num=transaction_number)
                add_new_item = Item(transaction_num=pulled_transaction, desc=item)
                add_new_item.save()
                new_item_id = item_id_query()
                new_item_ids.append(new_item_id)
        else:
            pulled_transaction = Transaction.objects.get(transaction_num=transaction_number)
            add_new_item = Item(transaction_num=pulled_transaction, desc=item_lists)
            add_new_item.save()
            new_item_id = item_id_query()
            new_item_ids.append(new_item_id)

        pulled_transaction = Transaction.objects.get(transaction_num=transaction_number)
        item_count = Item.objects.filter(transaction_num=pulled_transaction).count()

        logger.info('%s added items to Transaction # %s', request.user, transaction_number)

        return new_item_ids, item_count


def add_note(request):
    if request.POST.get('status') == 'add_note':
        blurb = request.POST.get('blurb')
        user_id = request.POST.get('user_id')
        transaction_number = request.POST.get('transaction_number')
        now = localtime()

        pulled_transaction = Transaction.objects.get(transaction_num=transaction_number)
        pulled_user = User.objects.get(pk=user_id)
        new_note = Note(transaction_num=pulled_transaction,
                        content=blurb, date=now, user=pulled_user)
        new_note.save()

        latest_note = Note.objects.latest('note_id')
        latest_note_date = localtime(latest_note.date)

        note_user = pulled_user.first_name

        logger.info('%s added a Note to Transaction # %s', request.user, transaction_number)

        note_count = Note.objects.filter(transaction_num=pulled_transaction).count()

        return (latest_note_date.strftime('%A, %b. %d, %Y, %I:%M %p'),
                note_count, note_user)


def edit_item(request):
    if request.POST.get('status') == 'edit_item':
        item_id = request.POST.get('current_item_id')
        new_desc = request.POST.get('new_desc')
        Item.objects.filter(itemid=item_id).update(desc=new_desc)

        logger.info('%s edited Item # %s', request.user, item_id)


def edit_item_date(request):
    if request.POST.get('status') == 'edit_item_date':
        item_id = request.POST.get('current_item_id')
        new_date = request.POST.get('new_date')
        transaction_number = request.POST.get('transaction_number')
        Item.objects.filter(itemid=item_id).update(picked_up_on=new_date)
        new_item_date = Item.objects.get(itemid=item_id)

        logger.info('%s changed Item #%s date to %s', request.user, item_id, new_date)

        return (new_item_date.status(), transaction_info(transaction_number))


def edit_transaction(request):
    if request.POST.get('status') == 'edit_transaction':
        transaction_number = request.POST.get('transaction_number')
        edited_transaction_number = request.POST.get('edited_transaction_number')
        transaction_date = request.POST.get('transaction_date')
        est_pickup_date = request.POST.get('est_pickup_date')
        customer_name = request.POST.get('customer_name')
        phone_number = request.POST.get('phone_number')

        returned_data = {
            'transaction_date': transaction_date,
            'est_pickup_date': est_pickup_date,
            'customer_name': customer_name,
            'phone': phone_number,
        }

        if transaction_number != edited_transaction_number:
            Transaction.objects.filter(transaction_num=transaction_number).update(
                transaction_num=edited_transaction_number)
            pulled_transaction = Transaction.objects.get(pk=edited_transaction_number)
            Item.objects.filter(transaction_num_id=transaction_number).update(
                transaction_num_id=pulled_transaction)
            Note.objects.filter(transaction_num_id=transaction_number).update(
                transaction_num_id=pulled_transaction)
            new_transaction_num = edited_transaction_number
        else:
            new_transaction_num = transaction_number

        for entry in returned_data:
            if returned_data[entry] != '':
                Transaction.objects.filter(transaction_num=new_transaction_num).update(
                    **{entry: returned_data[entry]})

        return new_transaction_num


def forfeit(request):
    if request.POST.get('status') == 'forfeit':
        transaction_number = request.POST.get('transaction_number')
        pulled_transaction = Transaction.objects.get(transaction_num=transaction_number)

        if pulled_transaction.forfeit_date is None:
            today = time.strftime('%Y-%m-%d')
            Transaction.objects.filter(
                transaction_num=transaction_number).update(forfeit_date=today)
        else:
            Transaction.objects.filter(
                transaction_num=transaction_number).update(forfeit_date=None)

        logger.info('%s forfeited transaction # %s', request.user, transaction_number)


def check_item(request):
    if request.POST.get('status') == 'check_item':
        item_to_check = request.POST.get('current_id')
        transaction_number = request.POST.get('transaction_number')

        pulled_item = Item.objects.get(itemid=item_to_check)

        if pulled_item.picked_up_on is None:
            pickup_day = time.strftime('%Y-%m-%d')
            Item.objects.filter(itemid=item_to_check).update(picked_up_on=pickup_day)
        else:
            Item.objects.filter(itemid=item_to_check).update(picked_up_on=None)

        pulled_item = Item.objects.get(itemid=item_to_check)
        item_status = pulled_item.status()
        item_date = pulled_item.picked_up_on

        if item_date is not None:
            item_date = item_date.strftime('%A, %b. %d, %Y')
        else:
            item_date = ''

        return (item_status, 0, transaction_info(transaction_number), item_date)


def remove_transaction(request):
    if request.POST.get('status') == 'remove_transaction':
        transaction_number = request.POST.get('transaction_number')
        pulled_transaction = Transaction.objects.get(transaction_num=transaction_number)
        pulled_transaction.delete()

        logger.info('%s removed transaction # %s', request.user, transaction_number)


# Views

@login_required
def transaction(request, trx=None):
    add_form = TransactionForm()

    if request.method == 'POST':
        edited_transaction = edit_transaction(request)
        if edited_transaction is not None:
            return HttpResponse(json.dumps(edited_transaction), content_type='application/json')

        edited_date = edit_item_date(request)
        if edited_date is not None:
            return HttpResponse(json.dumps(edited_date), content_type='application/json')

        item_count_response = trash_item(request)
        if item_count_response is not None:
            return HttpResponse(json.dumps(item_count_response), content_type='application/json')

        note_data = add_note(request)
        if note_data is not None:
            return HttpResponse(json.dumps(note_data), content_type='application/json')

        pk = add_item(request)
        if pk is not None:
            return HttpResponse(json.dumps(pk), content_type='application/json')

        item_info = check_item(request)
        if item_info is not None:
            return HttpResponse(json.dumps(item_info), content_type='application/json')

        edit_item(request)
        forfeit(request)
        remove_transaction(request)

        return JsonResponse({'status': 'ok'})

    data = {}
    try:
        t = get_object_or_404(Transaction, pk=trx)
        data['transaction_list'] = [t]
    except Transaction.DoesNotExist:
        return render(request, 'pickup/404.html', {'error_message': 'Transaction not found'}, status=404)

    n = Note.objects.filter(transaction_num=trx).order_by('-date')
    data['note_list'] = n
    data['add_form'] = add_form

    return render(request, 'pickup/transaction.html', data)


@login_required
def active(request):
    active_transactions = Transaction.objects.filter(
        forfeit_date__isnull=True).order_by('-transaction_date', '-transaction_num')
    active_items = Item.objects.filter(picked_up_on__isnull=True)

    context = {
        'transaction_list': active_transactions,
        'item_list': active_items,
    }

    return render(request, 'pickup/active.html', context)


@login_required
def archived(request):
    archived_transactions = Transaction.objects.filter(
        forfeit_date__isnull=False
    ).order_by('-forfeit_date', '-transaction_num')

    # Also include completed transactions (all items picked up, not forfeited)
    completed_transactions = []
    active_transactions = Transaction.objects.filter(forfeit_date__isnull=True)
    for trx in active_transactions:
        if trx.status() == 'Completed':
            completed_transactions.append(trx)

    context = {
        'forfeited_list': archived_transactions,
        'completed_list': completed_transactions,
    }
    return render(request, 'pickup/archived.html', context)


@login_required
def home(request):
    transactions = Transaction.objects.all().order_by('-transaction_date', '-transaction_num')
    overdue_list = [trx for trx in transactions if trx.overdue()]

    total_transactions = transactions.count()
    active_transactions = Transaction.objects.filter(forfeit_date__isnull=True)
    forfeited_count = Transaction.objects.filter(forfeit_date__isnull=False).count()

    # Compute statuses by iterating (status is a model method, not a DB field)
    status_counts = {'Active': 0, 'In Progress': 0, 'Completed': 0, 'No Items': 0}
    for trx in active_transactions:
        s = trx.status()
        if s in status_counts:
            status_counts[s] += 1

    total_items = Item.objects.count()
    items_in_inventory = Item.objects.filter(picked_up_on__isnull=True).count()
    items_picked_up = Item.objects.filter(picked_up_on__isnull=False).count()
    total_notes = Note.objects.count()

    context = {
        'overdue_transactions': len(overdue_list),
        'total_transactions': total_transactions,
        'active_count': status_counts['Active'],
        'in_progress_count': status_counts['In Progress'],
        'completed_count': status_counts['Completed'],
        'forfeited_count': forfeited_count,
        'total_items': total_items,
        'items_in_inventory': items_in_inventory,
        'items_picked_up': items_picked_up,
        'total_notes': total_notes,
    }

    return render(request, 'pickup/home.html', context)


@login_required
def profile(request):
    return render(request, 'pickup/profile.html')


class CustomLogoutView(LogoutView):
    next_page = 'login'


def handler404(request, exception=None):
    response = render(request, 'pickup/404.html', {})
    response.status_code = 404
    return response
