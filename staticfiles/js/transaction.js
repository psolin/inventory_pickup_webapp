// Get CSRF token from cookies (Django standard approach)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Set up CSRF token for all jQuery AJAX POST requests
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        }
    }
});

// Grab the transaction number
const transaction_number = $('[name="trans_num"]').attr('id');


// Function for updating info tab final pickup
function updateInfoPickup(status, pickup_date) {
    // Remove the existing actual pickup list item
    $('#info_actual_pickup').remove();

    // Only if the status is completed, add it back
    if (status === "Completed") {
        const final_pickup = $('<span>', {
            id: 'info_actual_pickup',
            html: $('<li>', {
                html: '<strong>Actual Pickup</strong>: ' + pickup_date
            })
        });

        // Throw it onto the info list
        $('#info_list').append(final_pickup);
    }
}


// Supposedly fixes a button glitch
$(".btn").mouseup(function() {
    $(this).blur();
});


// Check and uncheck item state
$('.item_state').click(function() {
    const this_checkbox = $(this);
    const item_id = $(this).attr('value');

    // Send data to the view via POST
    $.post('/transaction/' + transaction_number, {status: 'check_item', current_id: item_id, transaction_number: transaction_number}, function(data) {
        const item_status = data[0];
        const transaction_status = data[2][0];
        const pickup_date = data[2][1];
        const item_date = data[3];

        // Update the item's status
        $('#status-' + item_id).html(item_status);

        // Toggle the checkbox icon
        const icon = this_checkbox.find('i');
        if (icon.hasClass('bi-check-square')) {
            icon.removeClass('bi-check-square').addClass('bi-square');
            // Clear the modal date if unchecked
            $('#edit_pickupdate-' + item_id + "_hidden").val("");
            $('#edit_pickupdate-' + item_id).val("");
        } else {
            icon.removeClass('bi-square').addClass('bi-check-square');
            // Add the modal date if checked
            $('#edit_pickupdate-' + item_id).val(item_date);
        }

        // Update the status on the first tab
        $('#info_status').html(transaction_status);

        // Update the info tab
        updateInfoPickup(transaction_status, pickup_date);
    });
});


// Delete items — replaced .confirmation() plugin with native confirm()
$('[data-action="trash"]').click(function(event) {
    event.preventDefault();
    const button_id = $(this).attr('data-item-id');
    const item_name = $(this).attr('data-item-name');

    if (!confirm("Remove '" + item_name + "'?")) {
        return;
    }

    $.post('/transaction/' + transaction_number, {item_id: button_id, status: 'trash', transaction_number: transaction_number}, function(data) {
        const current_list_item = $('.list-group-item[id=' + button_id + ']');

        // Now that the database has been hit, remove the item from the DOM
        current_list_item.slideUp(500, function() { $(this).remove(); });

        // Update the count at the top
        const item_count = data[0];
        $('#item_count').html(item_count);

        const transaction_status = data[1][0];
        const pickup_date = data[1][1];

        // Update the status on the first tab
        $('#info_status').html(transaction_status);

        // Update the info tab
        updateInfoPickup(transaction_status, pickup_date);
    });
});


// Append new items
$('#save_new_items').click(function() {
    const item_names = $('#add_item_list').val();
    const item_name_list = item_names.split(',');

    // Send data to the view via POST
    $.post('/transaction/' + transaction_number, {status: 'add_item', item_list: item_names, transaction_number: transaction_number}, function(data) {

        const item_ids = data[0];
        const item_count = data[1];

        // The transaction status is made active simply by adding items
        const transaction_status = "Active";
        const pickup_date = "";

        // Update the status on the first tab
        $('#info_status').html(transaction_status);

        // Update the info tab
        updateInfoPickup(transaction_status, pickup_date);

        // Update the item count
        $('#item_count').html(item_count);

        for (let i = 0; i < item_name_list.length; i++) {
            const item_name = item_name_list[i];
            const current_item_id = data[0][i];

            const list_item = $('<li>', {
                class: 'list-group-item',
                id: current_item_id,
                html: $('<p>', {
                    html: $('<strong>', {
                        html: $('<span>', {
                            class: 'item_desc',
                            id: current_item_id,
                            html: item_name
                        })
                    })
                })
            });

            // Add the initial list item
            $('#item_list li:last').before(list_item);

            // Add status label
            const item_status_string = $('<p>', {
                id: 'item_list',
                html: $('<small>', {
                    class: 'item_status',
                    id: current_item_id,
                    html: 'In Inventory'
                })
            });

            // Initial checkbox button, which sends data back to the view
            const button_list = $('<p>', {
                html: $('<button/>', {
                    class: 'btn btn-sm btn-outline-secondary item_state',
                    id: 'item_state',
                    value: current_item_id,
                    html: '<i class="bi bi-square"></i>',
                    click: function() {
                        const this_checkbox = $(this);
                        const item_id = $(this).attr('value');

                        $.post('/transaction/' + transaction_number, {status: 'check_item', current_id: item_id, transaction_number: transaction_number}, function(data) {
                            const item_status = data[0];
                            const transaction_status = data[2][0];
                            const pickup_date = data[2][1];
                            const item_date = data[3];

                            const icon = this_checkbox.find('i');
                            if (icon.hasClass('bi-check-square')) {
                                icon.removeClass('bi-check-square').addClass('bi-square');
                                $('#info_status').html(transaction_status);
                                $('.item_status[id=' + item_id + ']').html(item_status);
                                updateInfoPickup(transaction_status, pickup_date);
                                $('#edit_pickupdate-' + current_item_id + "_hidden").val("");
                                $('#edit_pickupdate-' + current_item_id).val("");
                            } else {
                                icon.removeClass('bi-square').addClass('bi-check-square');
                                $('.item_status[id=' + item_id + ']').html(item_status);
                                $('#info_status').html(transaction_status);
                                updateInfoPickup(transaction_status, pickup_date);
                                $('#edit_pickupdate-' + current_item_id).val(item_date);
                            }
                        });
                    }
                })
            });

            const edit_button = '<small>'
                + '<button type="button" class="btn btn-sm btn-outline-secondary" data-bs-toggle="modal" data-bs-target="#editItem-' + current_item_id + '">'
                + '<i class="bi bi-pencil"></i>'
                + '</button>'
                + '</small>';

            const trash_button = $('<small>', {
                html: $('<button>', {
                    type: 'button',
                    class: 'btn btn-sm btn-outline-danger',
                    'data-action': 'trash',
                    'data-item-id': current_item_id,
                    'data-item-name': item_name,
                    html: '<i class="bi bi-trash3"></i>',
                    click: function(event) {
                        event.preventDefault();
                        if (!confirm("Remove '" + item_name + "'?")) {
                            return;
                        }
                        $.post('/transaction/' + transaction_number, {item_id: current_item_id, status: 'trash', transaction_number: transaction_number}, function(data) {
                            const current_list_item = $('.list-group-item[id=' + current_item_id + ']');
                            const item_count = data[0];
                            const transaction_status = data[1][0];
                            const pickup_date = data[1][1];

                            current_list_item.slideUp(500, function() { $(this).remove(); });
                            $('#item_count').html(item_count);
                            $('#info_status').html(transaction_status);
                            updateInfoPickup(transaction_status, pickup_date);
                        });
                    }
                })
            });

            // Append the edit and delete buttons onto the button_list variable
            button_list.append(edit_button);
            button_list.append(" ");
            button_list.append(trash_button);

            // Append the new list item with all of the relevant things
            $(list_item).append(item_status_string);
            $(list_item).append(button_list);

            const modal = '<div class="modal fade" id="editItem-' + current_item_id + '" tabindex="-1" aria-labelledby="editItem" aria-hidden="true">'
                + '<div class="modal-dialog">'
                + '<div class="modal-content">'
                + '<div class="modal-header">'
                + '<h5 class="modal-title">Edit Item</h5>'
                + '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>'
                + '</div>'
                + '<div class="modal-body">'
                + '<label for="editItem">Item Name</label>'
                + '<input id="edit_input-' + current_item_id + '" class="form-control input-group-lg reg_name" type="text" name="editItem" value="' + item_name + '">'
                + '<br />'
                + '<label for="editPickupDate">Pickup Date</label>'
                + '<input type="text" class="form-control datepicker" id="edit_pickupdate-' + current_item_id + '" name="editPickupDate" value="">'
                + '<input type="hidden" class="form-control hidden" id="edit_pickupdate-' + current_item_id + '_hidden" name="editPickupDateHidden">'
                + '</div>'
                + '<div class="modal-footer">'
                + '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>'
                + '<button type="button" class="btn btn-primary edit-item-button edit_item" data-bs-dismiss="modal" item-id="' + current_item_id + '">Edit</button>'
                + '</div>'
                + '</div>'
                + '</div>'
                + '</div>';

            // Append the modal to the DOM
            $(list_item).append(modal);

            // Initialize the bootstrap-datepicker on new elements
            $('#editItem-' + current_item_id + ' .datepicker').datepicker({
                format: 'DD, M. d, yyyy',
                autoclose: true,
                todayHighlight: true
            });

            $('.edit_item').click(function() {
                const current_item_id = $(this).attr("item-id");

                // Current / Edited descriptions
                const current_item_desc = $("#" + current_item_id + ".item_desc").text();
                const edited_item_desc = $('#edit_input-' + current_item_id).val();

                // Current / Edited time
                const current_item_date = $('#edit_pickupdate-' + current_item_id).attr('date');
                const edited_item_date = $('#edit_pickupdate-' + current_item_id + '_hidden').val();

                if (current_item_desc !== edited_item_desc) {
                    $.post('/transaction/' + transaction_number, {status: 'edit_item', current_item_id: current_item_id, new_desc: edited_item_desc}, function() {
                        const item_desc_tag = $('#' + current_item_id + '.item_desc');
                        $(item_desc_tag).html(edited_item_desc);
                    });
                }

                // Update the date if edited
                if (edited_item_date && edited_item_date !== current_item_date) {
                    $.post('/transaction/' + transaction_number, {status: 'edit_item_date', transaction_number: transaction_number, current_item_id: current_item_id, new_date: edited_item_date}, function(data) {
                        $('#edit_pickupdate-' + current_item_id).attr('date', edited_item_date);

                        const new_date_string = data[0];
                        const transaction_status = data[1][0];
                        const pickup_date = data[1][1];

                        $('.item_status[id="' + current_item_id + '"]').html(new_date_string);

                        const this_checkbox = $('.item_state[value="' + current_item_id + '"]');
                        this_checkbox.find('i').removeClass('bi-square').addClass('bi-check-square');

                        $('#info_status').html(transaction_status);
                        updateInfoPickup(transaction_status, pickup_date);
                    });
                }
            });
        }
    });
});


// Edit item modal jQuery
$('.edit_item').click(function() {
    const current_item_id = $(this).attr("item-id");

    // Current / Edited descriptions
    const current_item_desc = $("#" + current_item_id + ".item_desc").text();
    const edited_item_desc = $('#edit_input-' + current_item_id).val();

    // Current / Edited time
    const current_item_date = $(".item_status[id='status-" + current_item_id + "']").attr('date');
    const edited_item_date = $('#edit_pickupdate-' + current_item_id + '_hidden').val();

    if (current_item_desc !== edited_item_desc) {
        $.post('/transaction/' + transaction_number, {status: 'edit_item', current_item_id: current_item_id, new_desc: edited_item_desc}, function() {
            const item_desc_tag = $('#' + current_item_id + '.item_desc');
            $(item_desc_tag).html(edited_item_desc);
            $('#edit_input-' + current_item_id).val();
        });
    }

    // Update the date
    if (edited_item_date && edited_item_date !== current_item_date) {
        $.post('/transaction/' + transaction_number, {status: 'edit_item_date', transaction_number: transaction_number, current_item_id: current_item_id, new_date: edited_item_date}, function(data) {

            const new_date_string = data[0];
            const transaction_status = data[1][0];
            const pickup_date = data[1][1];

            $('#status-' + current_item_id).html(new_date_string);

            const this_checkbox = $('.item_state[value="' + current_item_id + '"]');
            this_checkbox.find('i').removeClass('bi-square').addClass('bi-check-square');

            $('#info_status').html(transaction_status);
            updateInfoPickup(transaction_status, pickup_date);
        });
    }
});


// Save new notes
$('#save_new_note').click(function() {
    const blurb = $('#textarea').val();
    const user_id = $('[class="user_credentials"]').attr('id');

    // Send data to the view via POST
    $.post('/transaction/' + transaction_number, {status: 'add_note', blurb: blurb, transaction_number: transaction_number, user_id: user_id}, function(data) {

        const note_date = data[0];
        const note_count = data[1];
        const note_user = data[2];
        $('#note_count').html(note_count);

        const list_note = $('<li>', {
            class: 'list-group-item',
            html: $('<p>', {
                html: blurb
            })
        });

        const list_footer = $('<p>', {
            html: $('<small>', {
                html: '- ' + note_user + ', ' + note_date
            })
        });

        list_note.append('<br>');
        list_note.append(list_footer);

        $('#note_list').prepend(list_note).slideDown();
    });
});


// Edit form reset
$('[name="edit_form_reset"]').click(function() {
    // Reset transaction number
    const transNum = $('[id="transNum"]').attr('initial');
    $('[id="transNum"]').val(transNum);

    // Reset transaction date
    const transDate = $('[id="transDate"]').attr('initial');
    $('[id="transDate"]').val(transDate);

    // Reset estimated pickup date
    let pickupDate = $('#editTransDate').attr('initial');
    let submitted_pickupDate = $('[id="editTransDate"]').attr('hiddeninitial');
    $('#editTransDate').val(pickupDate);
    $('#editTransDate_hidden').val(submitted_pickupDate);

    // Reset estimated pickup date
    pickupDate = $('#editpickupDate').attr('initial');
    submitted_pickupDate = $('[id="editpickupDate"]').attr('hiddeninitial');
    $('#editpickupDate').val(pickupDate);
    $('#editpickupDate_hidden').val(submitted_pickupDate);

    // Reset customer name
    const editCustomer = $('[id="editCustomer"]').attr('initial');
    $('[id="editCustomer"]').val(editCustomer);

    // Reset phone number
    const editPhone = $('#editPhone').attr('initial');
    $('[name="editPhone"]').val(editPhone);
});


// Forfeit/reinstate buttons — replaced .confirmation() with native confirm()
$('#forfeit_button').click(function() {
    if (!confirm('Are you sure you want to forfeit this transaction?')) {
        return;
    }

    $.post('/transaction/' + transaction_number, {status: 'forfeit', transaction_number: transaction_number}, function() {
        // Redirect to transaction page
        window.location.href = "/transaction/" + transaction_number;
    });
});


// Delete transaction button — replaced .confirmation() with native confirm()
$('#remove_transaction').click(function() {
    if (!confirm('Are you sure you want to permanently delete this transaction?')) {
        return;
    }

    $.post('/transaction/' + transaction_number, {status: 'remove_transaction', transaction_number: transaction_number}, function() {
        // Redirect to home page
        window.location.href = "/home/";
    });
});


// Edit form submission
$('#save_edits').click(function() {
    // Transaction Number
    const initial_transaction_number = $('#transNum').attr('initial');
    const edited_transaction_number = $('#transNum').val();

    // Transaction Date
    const initial_transaction_date = $('#editTransDate').attr('hiddeninitial');
    const edited_transaction_date = $('#editTransDate_hidden').val();

    // Est Pickup Date
    const initial_pickup_date = $('#editpickupDate').attr('hiddeninitial');
    const edited_pickup_date = $('#editpickupDate_hidden').val();

    // Customer Name
    const initial_customer_name = $('#editCustomer').attr('initial');
    const edited_customer_name = $('#editCustomer').val();

    // Phone Number
    const initial_phone = $('#editPhone').attr('initial');
    const edited_phone = $('#editPhone').val();

    // If there are changes, send the changes. Or else send an empty string.
    const sent_transaction_date = (initial_transaction_date !== edited_transaction_date) ? edited_transaction_date : "";
    const sent_pickup_date = (initial_pickup_date !== edited_pickup_date) ? edited_pickup_date : "";
    const sent_customer_name = (initial_customer_name !== edited_customer_name) ? edited_customer_name : "";
    const sent_phone = (initial_phone !== edited_phone) ? edited_phone : "";

    $.post('/transaction/' + transaction_number, {
        status: 'edit_transaction',
        transaction_number: initial_transaction_number,
        edited_transaction_number: edited_transaction_number,
        transaction_date: sent_transaction_date,
        est_pickup_date: sent_pickup_date,
        customer_name: sent_customer_name,
        phone_number: sent_phone
    }, function(data) {
        const returned_transaction_number = data;
        // Redirect to new transaction page
        window.location.href = "/transaction/" + returned_transaction_number;
    });
});
