$('.datepicker').pickadate({
    format: 'dddd, mmm. d, yyyy',
    formatSubmit: 'yyyy-mm-dd',
    today: '',
    clear: 'Clear',
    hiddenPrefix: 'prefix__',
    hiddenSuffix: '__suffix',
    hiddenName: true
});

$('[data-role="tagsinput"]').tagsinput({
  allowDuplicates: true
});

$('#add_transaction_button').click( function() {

	transaction_num = $('#id_transaction_num').val();
	transaction_date = $('#id_transaction_date_hidden').val();
	est_pickup_date = $('#id_est_pickup_date_hidden').val();
	customer_name = $('#id_customer_name').val();
	phone = $('#addPhone').val();
	items = $('#id_items').val()

	var pathname = String(window.location.pathname);

	if (transaction_num != '' && transaction_date != '' && est_pickup_date != '' && customer_name != '' && phone != '' && items != '') {

		$.get(pathname, {status: 'add_transaction', transaction_num: transaction_num, transaction_date: transaction_date, est_pickup_date: est_pickup_date, customer_name: customer_name, phone: phone, items: items}, function(data) {


		// Redirect to new transaction page
		window.location.href="/transaction/" + transaction_num;

	});

	}
	else {
		alert("Hey, you're missing information.")
	}
});