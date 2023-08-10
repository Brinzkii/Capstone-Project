function show_next_results(btn) {
	let page = btn.text();
	let results = $('.card-small');
	console.log(btn.text());
	
	$('.disabled').toggleClass('disabled')
	$(results).hide();
	$('.active').toggleClass('active')
	$(btn).parent().toggleClass('active')

	let low = (page * 50) - 49;
	let high = (page * 50)
	
	for (let i = low; i <= high; i++) {
		$(results[i]).show()
	}

	$(window).scrollTop(0);
	
}

$('body').on('click', '.page-link-num', function(evt) {
	evt.preventDefault();
	let btn = $(evt.target);
	
	show_next_results(btn);
});

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
