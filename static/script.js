function hide_extra_ingredient_fields() {
	for (let i = 2; i <= 15; i++) {
		$(`#ingredient${i}`).hide();
		$(`#measurement${i}`).hide();
	}
}

hide_extra_ingredient_fields();

function add_ingredient_fields() {
	let bottom = $('input.ing-form:visible').last();
	let del_btn = $('<i></i>');
	del_btn.addClass('bi bi-dash-circle');

	bottom.next().show();
	bottom.next().next().show();

	del_btn.insertBefore(bottom.next());

	hide_if_no_more();
}

function hide_if_no_more() {
	if ($('.ing-form:hidden').length === 0) {
		$('.bi-plus-lg').hide();
	}
}

$('.bi-plus-lg').on('click', add_ingredient_fields);

function remove_ingredient_fields(btn) {
	let next = $(btn.next());
	
	next.hide();
	next.next().val('');
	next.next().hide();
	btn.remove();
}

$('#ingredients_form').on('click', '.bi-dash-circle', function(evt) {
	let btn = $(evt.target);
	
	remove_ingredient_fields(btn);
});
