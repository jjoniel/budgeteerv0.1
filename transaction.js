// first row remove button
$(document).on('click', '.remove', function() {
    $(this).closest('tr').remove();
    updateTotal();
});

// form validation
$('#transaction-form').submit(function(event) {
    let isValid = true;
    $(this).find('input[type="text"], input[type="number"], select').each(function() {
        const $merchant = $('#merchant');
        const isMerchantNew = $merchant.val() === 'new';
        const isNewsElement = $(this).hasClass('news');

        const addingNew = $(this).closest('td').find('.unit').val() === 'new';
        const newUnit = $(this).hasClass('new-unit-name');
        const newSize = $(this).hasClass('new-unit-size');
        if(!addingNew && newUnit) {
            return true;
        }
        else if(newSize)
        {   
            return true;
        }

        if (!isMerchantNew && isNewsElement) {
            return true; 
        }

        if ($(this).val().trim() === '') {
            alert('Please fill in all fields.');
            console.log($(this))
            console.log($(this).attr('class'))
            console.log(addingNew)
            console.log(newUnit)
            isValid = false;
            return false;
        }
    });

    if (!isValid) {
        event.preventDefault();
    }
});

// add new merchant functionality
$('#merchant').on('change', function() {
    if ($(this).val() === 'new') {
        $('#new-merchant').show();
    } else {
        $('#new-merchant').hide();
    }
});

if ($('#merchant').val() === 'new') {
    $('#merchant').trigger('change');
}

// dynamically update totals
function updateTotal() {
    let total = 0;
    let count = 0
    $('.total-price').each(function() {
        const value = parseFloat($(this).val());
        if (!isNaN(value)) {
            total += value;
        }
        const value2 = parseInt($(this).closest('tr').find('.quantity').val())
        if (!isNaN(value2)) {
            count += value2;
        }
    });
    $('#total-amount').text(`$${total.toFixed(2)}`);
    $('#total-items').text(`${count}`);
}

$(document).on('input', '.total-price', updateTotal);
$(document).on('input', '.quantity', updateTotal);
updateTotal();

// add new unit functionality
$('.unit').on('change', function() {
    var selectedValue = $(this).val();
    if (selectedValue === 'new') {
        $(this).closest('tr').find('.new-unit-fields').css('visibility', 'visible');
    } else {
        $(this).closest('tr').find('.new-unit-fields').css('visibility', 'hidden');
    }
});
$('.unit').trigger('change');
