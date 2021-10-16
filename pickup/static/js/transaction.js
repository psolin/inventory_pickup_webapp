// Grab the transaction number
transaction_number = $('[name="trans_num"]').attr('id');


// Function for updaing info tab final pickup an item
var updateInfoPickup = function(status, pickup_date){ 


	//Remove the existing actual pickup list item
	$('#info_actual_pickup').remove();

	// Only if the status is completed, add it back
	if (status == "Completed"){

		final_pickup = $('<span>', {
			id: 'info_actual_pickup',
			html: $('<li>',{
				html: '<strong>Actual Pickup</strong>: ' + pickup_date
				})
		});

	// Throw it onto the info list
	$('#info_list').append(final_pickup);
	}

}


// Supposedly fixes a button glitch.  Who knows?
$(".btn").mouseup(function(){
    $(this).blur();
});


// Check and uncheck item state
$('.item_state').click(function() {
	this_checkbox = $(this);
	item_id = $(this).attr('value');

	// Send data to the view, and get it back with "data"
	$.get('/transaction/' + transaction_number, {status: 'check_item', current_id: item_id, transaction_number: transaction_number}, function(data) {
		item_status = data[0];
		active_transactions = data[1];
		transaction_status = data[2][0];
		pickup_date = data[2][1];
		item_date = data[3];

		// Update the item's status
		$('#status-' + item_id).html(item_status);

		// Change the button if it has been clicked
		if (this_checkbox.attr('class') == "btn btn-default glyphicon glyphicon-check item_state" ) {
			$(this_checkbox).attr('class', 'btn btn-default glyphicon glyphicon-unchecked item_state');
			
			// Clear the modal date if unchecked
			$('#edit_pickupdate-' + item_id + "_hidden").val("");
			$('#edit_pickupdate-' + item_id).val("");

		}
		else{
			$(this_checkbox).attr('class', 'btn btn-default glyphicon glyphicon-check item_state');

			// Add the modal date if checked
			$('#edit_pickupdate-' + item_id).val(item_date);

		}

		// Update the status on the first tab
		$('#info_status').html(transaction_status);

		// Update the info tab
		updateInfoPickup(transaction_status, pickup_date);
		

	})
 });


// Delete items
$('[data-toggle="confirmation"]').confirmation({
	onConfirm: function(event) {
		// Stop the page from jumping around
		event.preventDefault();
		var button_function = $(this).attr('button');
		var button_id = $(this).attr('id');
		var transaction_number = $(this).attr('transnum');	
		
		$.get('/transaction/' + transaction_number, {item_id: button_id, status: button_function, transaction_number: transaction_number}, function(data) {
			
			current_list_item = $('.list-group-item[id=' + button_id + ']');

			// Now that the database has been hit, remove the item from the DOM
			current_list_item.slideUp(500, function() { $(this).remove(); });
			
			// Update the count at the top
			item_count = data[0];
			$('#item_count').html(item_count);

			transaction_status = data[1][0];
			pickup_date = data[1][1];

			// Update the status on the first tab
			$('#info_status').html(transaction_status);

			// Update the info tab
			updateInfoPickup(transaction_status, pickup_date);

		});
	},
	onCancel: function(event) { 
		// do nothing, really.
	}
});


// Append new items
$('#save_new_items').click(function() {
	item_names = $('#add_item_list').val();
	// Make a new JS list out of the items
	item_name_list = item_names.split(',');

	// Send data to the view, and get it back with "data"
	$.get('/transaction/' + transaction_number, {status: 'add_item', item_list: item_names, transaction_number: transaction_number}, function(data) {

		item_ids = data[0];
		item_count = data[1];

		// The transaction status is made active simply by adding items
		transaction_status = "Active";
		pickup_date = ""

		// Update the status on the first tab
		$('#info_status').html(transaction_status);

		// Update the info tab
		updateInfoPickup(transaction_status, pickup_date);
		
		$('#info_status').html(transaction_status);

		// Update the item count
		$('#item_count').html(item_count);

		// return 
		for(var i=0; i<item_name_list.length; i++) {

			var item_name = item_name_list[i];

			current_item_id = data[0][i];

			list_item = $('<li>', {
				class: 'list-group-item',
				id: current_item_id,
				html: $('<p>',{
					html: $('<strong>',{
						html: $('<span>',{
							class: 'item_desc',
							id: current_item_id,
							html: item_name
						})
					})
				})
			})

			// Add the initial list item
			$('#item_list li:last').before(
				//item_string,check_button
				list_item
				);

			// Add x in the list item
			item_status_string = $('<p>', {
				id: 'item_list',
				html: $('<small>', {
					class: 'item_status',
					id: current_item_id,
					html: 'In Inventory'
				})
				});

		// Initial checkbox button, which sends data back to the view	
		button_list = $('<p>', {
			html: $('<button/>',{
				class: 'btn btn-default glyphicon glyphicon-unchecked item_state',
				id: 'item_state',
				value: current_item_id,
				html: '<i class="icon-user icon-white"></i>',
				click: function () { 
						this_checkbox = $(this);
						item_id = $(this).attr('value');

						// Send data to the view, and get it back with "data"
						$.get('/transaction/' + transaction_number, {status: 'check_item', current_id: item_id, transaction_number: transaction_number}, function(data) {
							item_status = data[0];
							active_transactions = data[1];
							transaction_status = data[2][0];
							pickup_date = data[2][1];
							item_date = data[3];

							// Change the button if it has been clicked
							if (this_checkbox.attr('class') == "btn btn-default glyphicon glyphicon-check item_state" ) {
								$(this_checkbox).attr('class', 'btn btn-default glyphicon glyphicon-unchecked item_state');
								
								// Update the status on the first tab
								$('#info_status').html(transaction_status);

								// Update the item's status
								$('.item_status[id=' + item_id + ']').html(item_status);
	
								// Update the info tab
								updateInfoPickup(transaction_status, pickup_date);

								// Clear the modal date if unchecked
								$('#edit_pickupdate-' + current_item_id + "_hidden").val("");
								$('#edit_pickupdate-' + current_item_id).val("");
							}
							else{
								$(this_checkbox).attr('class', 'btn btn-default glyphicon glyphicon-check item_state');
								
								// Update the item's status
								$('.item_status[id=' + item_id + ']').html(item_status);

								// Update the status on the first tab
								$('#info_status').html(transaction_status);

								// Update the info tab
								updateInfoPickup(transaction_status, pickup_date);

								// Update the date in the modal
								
							$('#edit_pickupdate-' + current_item_id).val(item_date);


							}
							

						})
					}
				})
			});

			edit_button = '<small>'
			+ '<button type="button" class="btn btn-sm btn-default glyphicon glyphicon-pencil" data-toggle="modal" data-target="#editItem-' + current_item_id + '" data-button="edit" id="' + current_item_id + '">'
			+ '</button>'
			+ '</small>';

			

			trash_button = $('<small>', {
				html: $('<button>', {
					type: 'button',
					class: 'btn btn-sm btn-default glyphicon glyphicon-trash',
					id: current_item_id
				})
			});

			// Append the edit and delete buttons onto the button_list variable
			button_list.append(edit_button);
			button_list.append(" ");
			button_list.append(trash_button);

			// Append the new list item with all of the relevant things!
			// Append the item status!
			$(list_item).append(item_status_string);
			
			// Append the buttons!
			$(list_item).append(button_list);

			// Function for trashing an item
			var trashItem = function(current_id, trash_button, current_item){
			  
		    	$('.glyphicon-trash[id=' + current_id + ']').confirmation({
					title: "Remove '" + current_item + "'?",
					placement: 'bottom',
					onConfirm: function(event) {
						
						transaction_number = $('[name="trans_num"]').attr('id');
						
						$.get('/transaction/' + transaction_number, {item_id: current_id, status: 'trash', transaction_number: transaction_number}, function(data) {

							current_list_item = $('.list-group-item[id=' + current_id + ']');
							item_count = data[0];
							transaction_status = data[1][0];
							pickup_date = data[1][1];


							// Now that the database has been hit, remove the item from the DOM
							current_list_item.slideUp(500, function() { $(this).remove(); });
							
							// Update the count at the top
							$('#item_count').html(item_count);

							// Update the status on the first tab
							$('#info_status').html(transaction_status);

							// Update the info tab
							updateInfoPickup(transaction_status, pickup_date);

						});
					}
				});	    
			};

			// On clicking the trash button, run the trash function above
			$(trash_button).click(trashItem(current_item_id, trash_button, item_name));
				
			modal = '<div class="modal fade" id="editItem-' + current_item_id + '" tabindex="-1" role="dialog" aria-labelledby="editItem" aria-hidden="true">'
			  + '<div class="modal-dialog">'
			   + '<div class="modal-content">'
			     + '<div class="modal-header">'
			      + '<button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>'
			       + '<h4 class="modal-title" id="myModalLabel">Edit Item</h4>'
			      + '</div>'
			      + '<div class="modal-body">'
			      +	'<label for="editItem">Item Name</label>'
			      +	'<input id="edit_input-' + current_item_id + '" class="form-control input-group-lg reg_name" type="text" name="editItem" value="' + item_name + '">'
			      +	'<br />'
			      + '<label for="editPickupDate">Pickup Date</label>'
		          + '<input type="text" class="form-control datepicker" id="edit_pickupdate-' + current_item_id + '" name="editPickupDate" date="" value="">'
		          + '<input type="hidden" class="form-control datepicker hidden" id="edit_pickupdate-' + current_item_id + '" name="prefix__editPickupDate__suffix">'
			     + '</div>'
			     + '<div class="modal-footer">'
			      + '<button type="button" class="btn btn-default" data-dismiss="modal">Close</button><button type="button" class="btn btn-primary edit-item-button edit_item" data-dismiss="modal" id="edit_item" item-id="' + current_item_id + '">Edit</button>'
			     + '</div>'
			   + '</div>'
			 + '</div>'
			+ '</div>';
			
			// Append the modal to the DOM
			$(list_item).append(modal);

			// Remind that pesky datepicker who is boss
			$('.datepicker').pickadate({
			    format: 'dddd, mmm. d, yyyy',
			    formatSubmit: 'yyyy-mm-dd',
			    today: '',
			    clear: 'Clear',
			    hiddenPrefix: 'prefix__',
			    hiddenSuffix: '__suffix',
			    hiddenName: true
			});
	
			// I know that this is a huge waste of code but I needed to get this modal editing working
			// So, one day, I will just make this a function and it will work a bit quicker.
			// For now, I had to do what I had to do.  I have to live with it.
			// If you're better at me with jQuery, by all means, work your magic.
			// It will be much appreciated.

			$('.edit_item').click(function() {
				current_item_id = $(this).attr("item-id");

				// Current / Edited descriptions
				current_item_desc = $("#" + current_item_id + ".item_desc").text();
				edited_item_desc = $('#edit_input-' + current_item_id).val();

				// Current / Edited time
				current_item_date = $('#edit_pickupdate-' + current_item_id).attr('date');
				edited_item_date = $('#edit_pickupdate-' + current_item_id + '_hidden').val();			

				if (current_item_desc != edited_item_desc) {
					$.get('/transaction/' + transaction_number, {status: 'edit_item', current_item_id: current_item_id, new_desc: edited_item_desc}, function(data) {
						item_desc_tag = $('#' + current_item_id + '.item_desc');
						// Update the item description
						$(item_desc_tag).html(edited_item_desc);

						// Update the modal to reflect the change
						edited_item_desc = $('#edit_input-' + current_item_id).val();
					})
				}

				// Update the date if edited
				if (edited_item_date != current_item_date) {

					$.get('/transaction/' + transaction_number, {status: 'edit_item_date', transaction_number: transaction_number, current_item_id: current_item_id, new_date: edited_item_date}, function(data) {
					
						// Update the current date with what was sent to the view
						current_item_date = $('#edit_pickupdate-' + current_item_id).attr('date', edited_item_date);

						new_date_string = data[0];
						transaction_status = data[1][0];
						pickup_date = data[1][1];

						// Update the item page
						$('.item_status[id="' + current_item_id + '"]').html(new_date_string);
						
						this_checkbox = $('.item_state[value="' + current_item_id + '"]');

						// Change the button as if it has been clicked
						$(this_checkbox).attr('class', 'btn btn-default glyphicon glyphicon-check item_state');
						
						// Update the status on the first tab
						$('#info_status').html(transaction_status);

						// Update the info tab
						updateInfoPickup(transaction_status, pickup_date);
				})
			}
			}); // end current_edit_button			
		}
	})
});


// Edit item modal jQuery -->
$('.edit_item').click(function() {
	current_item_id = $(this).attr("item-id");
	
	// Current / Edited descriptions
	current_item_desc = $("#" + current_item_id + ".item_desc").text();
	edited_item_desc = $('#edit_input-' + current_item_id).val();

	// Current / Edited time
	current_item_date = $(".item_status[id='status-" + current_item_id+"']").attr('date');
	edited_item_date = $('#edit_pickupdate-' + current_item_id + '_hidden').val();

	if (current_item_desc != edited_item_desc) {
		$.get('/transaction/' + transaction_number, {status: 'edit_item', current_item_id: current_item_id, new_desc: edited_item_desc}, function(data) {
			item_desc_tag = $('#' + current_item_id + '.item_desc');
			// Update the item description
			$(item_desc_tag).html(edited_item_desc);

			// Update the modal to reflect the change
			edited_item_desc = $('#edit_input-' + current_item_id).val();
		})
	}
	

	// Update the date
	if (edited_item_date != current_item_date) {
		$.get('/transaction/' + transaction_number, {status: 'edit_item_date', transaction_number: transaction_number, current_item_id: current_item_id, new_date: edited_item_date}, function(data) {
			
			new_date_string = data[0];
			transaction_status = data[1][0];
			pickup_date = data[1][1];

			$('#status-' +  + current_item_id).html(new_date_string);
			
			this_checkbox = $('.item_state[value="' + current_item_id + '"]');

			// Change the button if it has been clicked
			$(this_checkbox).attr('class', 'btn btn-default glyphicon glyphicon-check item_state');
			
			// Update the status on the first tab
			$('#info_status').html(transaction_status);

			// Update the info tab
			updateInfoPickup(transaction_status, pickup_date);

		

		})
	}
});


// Save new notes
$('#save_new_note').click(function() {
	// Grab that blurb
	blurb = $('#textarea').val();

	// Grab the user id

	user_id = $('[class="user_credentials"]').attr('id');

	// Send data to the view, and get it back with "data"
	$.get('/transaction/' + transaction_number, {status: 'add_note', blurb: blurb, transaction_number: transaction_number, user_id: user_id}, function(data) {

		note_date = data[0];
		note_count = data[1];
		note_user = data[2]
		$('#note_count').html(note_count);

		list_note = $('<li>', {
			class: 'list-group-item',
			html: $('<p>',{
				html: blurb
			})
		});

		list_footer = $('<p>', {
			id: 'item_list',
			html: $('<small>', {
				html: '- ' + note_user + ', ' + note_date 
			})
		});

		list_note.append('<br>')
		list_note.append(list_footer)

		$('#note_list').prepend(
				list_note
				).slideDown();

		});


	
});


// Edit form reset
$('[name="edit_form_reset"]').click( function () {

	// Reset transaction number
	transNum = $('[id="transNum"]').attr('initial');
	$('[id="transNum"]').val(transNum);

	// Reset transaction date
	transDate = $('[id="transDate"]').attr('initial');
	$('[id="transDate"]').val(transDate);


	// Reset estimated pickup date
	pickupDate = $('#editTransDate').attr('initial');
	submitted_pickupDate = $('[id="editTransDate"]').attr('hiddeninitial');
	$('#editTransDate').val(pickupDate);
	// Reset hidden value, too.
	$('#editTransDate_hidden').val(submitted_pickupDate);

	// Reset estimated pickup date
	pickupDate = $('#editpickupDate').attr('initial');
	submitted_pickupDate = $('[id="editpickupDate"]').attr('hiddeninitial');
	$('#editpickupDate').val(pickupDate);
	// Reset hidden value, too.
	$('#editpickupDate_hidden').val(submitted_pickupDate);

	// Reset customer name
	editCustomer = $('[id="editCustomer"]').attr('initial');
	$('[id="editCustomer"]').val(editCustomer);

	// Reset phone number
	editPhone = $('#editPhone').attr('initial');
	$('[name="editPhone"]').val(editPhone);

}
);


// Forfeit/reinstate buttons
$('#forfeit_button').confirmation({
	placement: 'bottom',
	title: 'Are you sure?',
	btnOkLabel: 'Yes',
	btnCancelLabel: 'Cancel',
	onConfirm: function(){

		$.get('/transaction/' + transaction_number, {status: 'forfeit', transaction_number: transaction_number}, function(data) {

			// Redirect to transaction page
			window.location.href="/transaction/" + transaction_number;

		});
	}
	});


// Delete transaction button
$('#remove_transaction').confirmation({
	placement: 'bottom',
	title: 'Are you sure?',
	btnOkLabel: 'Yes',
	btnCancelLabel: 'Cancel',
	onConfirm: function(){

		$.get('/transaction/' + transaction_number, {status: 'remove_transaction', transaction_number: transaction_number}, function(data) {

			// Redirect to home page
			window.location.href="/home/";

		});
	}
	});


// Edit form submission
$('#save_edits').click( function () {
	
	// Transaction Number
	initial_transaction_number = $('#transNum').attr('initial');
	edited_transaction_number = $('#transNum').val();

	// Transaction Date
	initial_transaction_date = $('#editTransDate').attr('hiddeninitial');
	edited_transaction_date = $('#editTransDate_hidden').val();

	// Est Pickup Date
	initial_pickup_date = $('#editpickupDate').attr('hiddeninitial');
	edited_pickup_date = $('#editpickupDate_hidden').val();

	// Customer Name
	initial_customer_name = $('#editCustomer').attr('initial');
	edited_customer_name = $('#editCustomer').val();

	// Phone Number
	initial_phone = $('#editPhone').attr('initial');
	edited_phone = $('#editPhone').val();

	// If there are changes, send the changes.  Or else send an empty string.

	// Transaction Date
	if (initial_transaction_date != edited_transaction_date) {
		sent_transaction_date = edited_transaction_date;
	}
	else {
		sent_transaction_date = "";
	}

	// Est Pickup Date
	if (initial_pickup_date != edited_pickup_date) {
		sent_pickup_date = edited_pickup_date;
	}
	else {
		sent_pickup_date = "";
	}

	// Customer Name
	if (initial_customer_name != edited_customer_name) {
		sent_customer_name = edited_customer_name;
	}
	else {
		sent_customer_name = "";
	}

	// Phone Number
	if (initial_phone != edited_phone) {
		sent_phone = edited_phone;
	}
	else {
		sent_phone = "";
	}


	$.get('/transaction/' + transaction_number, {status: 'edit_transaction', transaction_number: initial_transaction_number, edited_transaction_number: edited_transaction_number, transaction_date: sent_transaction_date, est_pickup_date: sent_pickup_date, customer_name: sent_customer_name, phone_number: sent_phone}, function(data) {

			returned_transaction_number = data;
			// Redirect to new transaction page
			window.location.href="/transaction/" + returned_transaction_number;

	});

});