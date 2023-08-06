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

	del_btn.insertAfter(bottom);

	hide_if_no_more();
}

function remove_ingredient_fields(btn) {
	btn.next().hide();
	btn.next().next().hide();
}

function hide_if_no_more() {
	if ($('.ing-form:hidden').length === 0) {
		$('.bi-plus-lg').hide();
	}
}

$('.bi-plus-lg').on('click', add_ingredient_fields);

$('.bi-dash-circle').on('click', function (e) {
	remove_ingredient_fields(e.target);
	console.log('clicked');
});
