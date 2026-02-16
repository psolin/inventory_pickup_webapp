from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from pickup.models import Transaction, Item, Note
from pickup.forms import TransactionForm, ItemForm, SignUpForm, EditProfileForm


class TransactionModelTest(TestCase):
    def setUp(self):
        self.transaction = Transaction.objects.create(
            transaction_num=1001,
            customer_name='John Doe',
            transaction_date=date.today(),
            phone='(555) 123-4567',
            est_pickup_date=date.today() + timedelta(days=7),
        )

    def test_str(self):
        self.assertEqual(str(self.transaction), '1001')

    def test_status_no_items(self):
        self.assertEqual(self.transaction.status(), 'No Items')

    def test_status_active(self):
        Item.objects.create(itemid=1, transaction_num=self.transaction, desc='Chair')
        self.assertEqual(self.transaction.status(), 'Active')

    def test_status_in_progress(self):
        Item.objects.create(itemid=1, transaction_num=self.transaction, desc='Chair', picked_up_on=date.today())
        Item.objects.create(itemid=2, transaction_num=self.transaction, desc='Table')
        self.assertEqual(self.transaction.status(), 'In Progress')

    def test_status_completed(self):
        Item.objects.create(itemid=1, transaction_num=self.transaction, desc='Chair', picked_up_on=date.today())
        self.assertEqual(self.transaction.status(), 'Completed')

    def test_status_forfeited(self):
        self.transaction.forfeit_date = date.today()
        self.transaction.save()
        Item.objects.create(itemid=1, transaction_num=self.transaction, desc='Chair')
        self.assertEqual(self.transaction.status(), 'Forfeited')

    def test_final_pickup_date_when_completed(self):
        pickup = date(2025, 6, 15)
        Item.objects.create(itemid=1, transaction_num=self.transaction, desc='Chair', picked_up_on=pickup)
        result = self.transaction.final_pickup_date()
        self.assertIsNotNone(result)
        self.assertIn('Jun', result)

    def test_final_pickup_date_when_not_completed(self):
        Item.objects.create(itemid=1, transaction_num=self.transaction, desc='Chair')
        self.assertIsNone(self.transaction.final_pickup_date())

    def test_overdue_true(self):
        self.transaction.est_pickup_date = date.today() - timedelta(days=1)
        self.transaction.save()
        Item.objects.create(itemid=1, transaction_num=self.transaction, desc='Chair')
        self.assertTrue(self.transaction.overdue())

    def test_overdue_false_future_date(self):
        Item.objects.create(itemid=1, transaction_num=self.transaction, desc='Chair')
        self.assertFalse(self.transaction.overdue())

    def test_overdue_false_when_completed(self):
        self.transaction.est_pickup_date = date.today() - timedelta(days=1)
        self.transaction.save()
        Item.objects.create(itemid=1, transaction_num=self.transaction, desc='Chair', picked_up_on=date.today())
        self.assertFalse(self.transaction.overdue())


class ItemModelTest(TestCase):
    def setUp(self):
        self.transaction = Transaction.objects.create(
            transaction_num=2001,
            customer_name='Jane Doe',
            transaction_date=date.today(),
            phone='(555) 987-6543',
            est_pickup_date=date.today() + timedelta(days=7),
        )

    def test_str(self):
        item = Item.objects.create(itemid=1, transaction_num=self.transaction, desc='Sofa')
        self.assertEqual(str(item), 'Sofa')

    def test_status_in_inventory(self):
        item = Item.objects.create(itemid=1, transaction_num=self.transaction, desc='Sofa')
        self.assertEqual(item.status(), 'In Inventory')

    def test_status_picked_up(self):
        item = Item.objects.create(itemid=1, transaction_num=self.transaction, desc='Sofa', picked_up_on=date.today())
        self.assertEqual(item.status(), 'Picked Up')

    def test_status_forfeited(self):
        self.transaction.forfeit_date = date.today()
        self.transaction.save()
        item = Item.objects.create(itemid=1, transaction_num=self.transaction, desc='Sofa')
        self.assertEqual(item.status(), 'Forfeited')


class NoteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.transaction = Transaction.objects.create(
            transaction_num=3001,
            customer_name='Bob Smith',
            transaction_date=date.today(),
            phone='(555) 111-2222',
            est_pickup_date=date.today() + timedelta(days=7),
        )

    def test_str(self):
        note = Note.objects.create(
            note_id=1,
            transaction_num=self.transaction,
            content='Test note',
            date=timezone.now(),
            user=self.user,
        )
        self.assertEqual(str(note), '1')

    def test_cascade_delete(self):
        Note.objects.create(
            note_id=1,
            transaction_num=self.transaction,
            content='Test note',
            date=timezone.now(),
            user=self.user,
        )
        self.transaction.delete()
        self.assertEqual(Note.objects.count(), 0)


class TransactionFormTest(TestCase):
    def test_valid_form(self):
        form = TransactionForm(data={
            'transaction_num': 5001,
            'transaction_date': '2025-01-15',
            'est_pickup_date': '2025-01-22',
            'customer_name': 'Test Customer',
            'phone': '(555) 000-1111',
        })
        self.assertTrue(form.is_valid())

    def test_missing_transaction_num(self):
        form = TransactionForm(data={
            'transaction_date': '2025-01-15',
            'customer_name': 'Test Customer',
        })
        self.assertFalse(form.is_valid())


class SignUpFormTest(TestCase):
    def test_valid_signup(self):
        form = SignUpForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        form = SignUpForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'SecurePass123!',
            'password2': 'DifferentPass456!',
        })
        self.assertFalse(form.is_valid())


class AuthViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_logout_redirects(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_signup_page_loads(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_signup_creates_user(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())


class ProtectedViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_home_requires_login(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_home_loads_when_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_active_requires_login(self):
        response = self.client.get(reverse('active'))
        self.assertEqual(response.status_code, 302)

    def test_active_loads_when_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('active'))
        self.assertEqual(response.status_code, 200)

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)

    def test_profile_loads_when_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_transaction_requires_login(self):
        t = Transaction.objects.create(
            transaction_num=9001,
            customer_name='Test',
            transaction_date=date.today(),
            est_pickup_date=date.today(),
        )
        response = self.client.get(reverse('transaction', args=[9001]))
        self.assertEqual(response.status_code, 302)

    def test_transaction_loads_when_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        Transaction.objects.create(
            transaction_num=9001,
            customer_name='Test',
            transaction_date=date.today(),
            est_pickup_date=date.today(),
        )
        response = self.client.get(reverse('transaction', args=[9001]))
        self.assertEqual(response.status_code, 200)


class AddTransactionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_add_transaction_requires_post(self):
        response = self.client.get(reverse('add_transaction'))
        self.assertEqual(response.status_code, 405)

    def test_add_transaction_ajax(self):
        response = self.client.post(
            reverse('add_transaction'),
            {
                'transaction_num': 7001,
                'transaction_date': '2025-01-15',
                'est_pickup_date': '2025-01-22',
                'customer_name': 'AJAX Customer',
                'phone': '(555) 999-8888',
                'items': 'Chair,Table',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Transaction.objects.filter(transaction_num=7001).exists())
        self.assertEqual(Item.objects.filter(transaction_num=7001).count(), 2)

    def test_add_transaction_single_item(self):
        response = self.client.post(
            reverse('add_transaction'),
            {
                'transaction_num': 7002,
                'transaction_date': '2025-01-15',
                'est_pickup_date': '2025-01-22',
                'customer_name': 'Single Item Customer',
                'phone': '(555) 777-6666',
                'items': 'Lamp',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Item.objects.filter(transaction_num=7002).count(), 1)

    def test_check_transaction_num(self):
        Transaction.objects.create(
            transaction_num=8001,
            customer_name='Existing',
            transaction_date=date.today(),
            est_pickup_date=date.today(),
        )
        response = self.client.get(
            reverse('check_transaction_num'),
            {'transaction_num': 8001},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['exists'])

    def test_check_transaction_num_not_exists(self):
        response = self.client.get(
            reverse('check_transaction_num'),
            {'transaction_num': 99999},
        )
        self.assertFalse(response.json()['exists'])


class TransactionOperationsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', first_name='Test'
        )
        self.client.login(username='testuser', password='testpass123')
        self.transaction = Transaction.objects.create(
            transaction_num=6001,
            customer_name='Operations Test',
            transaction_date=date.today(),
            phone='(555) 333-4444',
            est_pickup_date=date.today() + timedelta(days=7),
        )
        self.item = Item.objects.create(
            itemid=100, transaction_num=self.transaction, desc='Test Item'
        )

    def test_trash_item(self):
        response = self.client.post(
            reverse('transaction', args=[6001]),
            {'status': 'trash', 'item_id': 100, 'transaction_number': 6001},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Item.objects.filter(itemid=100).exists())

    def test_check_item_pickup(self):
        response = self.client.post(
            reverse('transaction', args=[6001]),
            {'status': 'check_item', 'current_id': 100, 'transaction_number': 6001},
        )
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertIsNotNone(self.item.picked_up_on)

    def test_check_item_uncheck(self):
        self.item.picked_up_on = date.today()
        self.item.save()
        response = self.client.post(
            reverse('transaction', args=[6001]),
            {'status': 'check_item', 'current_id': 100, 'transaction_number': 6001},
        )
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertIsNone(self.item.picked_up_on)

    def test_edit_item_desc(self):
        response = self.client.post(
            reverse('transaction', args=[6001]),
            {'status': 'edit_item', 'current_item_id': 100, 'new_desc': 'Updated Item'},
        )
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(self.item.desc, 'Updated Item')

    def test_add_note(self):
        response = self.client.post(
            reverse('transaction', args=[6001]),
            {
                'status': 'add_note',
                'blurb': 'Test note content',
                'user_id': self.user.pk,
                'transaction_number': 6001,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Note.objects.filter(transaction_num=self.transaction).exists())

    def test_forfeit_transaction(self):
        response = self.client.post(
            reverse('transaction', args=[6001]),
            {'status': 'forfeit', 'transaction_number': 6001},
        )
        self.assertEqual(response.status_code, 200)
        self.transaction.refresh_from_db()
        self.assertIsNotNone(self.transaction.forfeit_date)

    def test_reinstate_transaction(self):
        self.transaction.forfeit_date = date.today()
        self.transaction.save()
        response = self.client.post(
            reverse('transaction', args=[6001]),
            {'status': 'forfeit', 'transaction_number': 6001},
        )
        self.assertEqual(response.status_code, 200)
        self.transaction.refresh_from_db()
        self.assertIsNone(self.transaction.forfeit_date)

    def test_remove_transaction(self):
        response = self.client.post(
            reverse('transaction', args=[6001]),
            {'status': 'remove_transaction', 'transaction_number': 6001},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Transaction.objects.filter(transaction_num=6001).exists())


class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123',
            first_name='Test', last_name='User', email='test@example.com'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_profile_edit_get(self):
        response = self.client.get(reverse('profile_edit'))
        self.assertEqual(response.status_code, 200)

    def test_profile_edit_post(self):
        response = self.client.post(reverse('profile_edit'), {
            'username': 'testuser',
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')
