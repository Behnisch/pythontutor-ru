function submit_solution(problem_name, code, callback) {
	var req = $.post('/tester/submit/', {
		problem: problem_name,
		user_code: code
	});

	req.done(function(res) {
		callback(true, res);
	});

	req.fail(function() {
		callback(false);
	});
}


var visualizer;

$(function() {
	var code = undefined;
	var stdin = $('.example_tests pre.input:first').text();

	var problem_saved = JSON.parse(localStorage.getItem('problem[' + problem_name + ']'));
	if(problem_saved !== null && problem_saved.solution !== undefined) {
		if(problem_saved.solution.code != '') {
			code = problem_saved.solution.code;
		}
		if(problem_saved.solution.stdin != '') {
			stdin = problem_saved.solution.stdin;
		}
	}


	visualizer = new Visualizer('#visualizer', code, stdin, {
		explain_mode: false
	});

	visualizer.focusCodeEditor();

	visualizer.on('change_code', function() {
		$('.submit_solution').toggle(visualizer.code.trim() != '');
	});


	setInterval(function() {
		localStorage.setItem('problem[' + problem_name + ']', JSON.stringify({
			solution: {
				code: visualizer.code,
				stdin: visualizer.stdin
			},
		}));
	}, 1000);


	$('.submit_solution').toggle((code || '').trim() != '');

	$('.submit_solution button').click(function() {
		var test_rows = $('#example_tests > tbody > tr')

		var button = $(this);
		var initial_text = button.html();

		button.attr('disabled', true).html('<span class="glyphicon glyphicon-time"></span> Решение отправляется...');

		submit_solution(problem_name, visualizer.code, function(success, result) {
			button.attr('disabled', false).html(initial_text);

			if(!success) {
				alert('Ой! Не удалось выполнить запрос к серверу :(');
				return;
			}

			$('#example_tests .test_result').show();

			$.each(result.tests, function(id, result) {
				test_rows[id] = $(test_rows[id]);

				var clazz, image, text;

				if(result == 'ok') {
					clazz = 'success';
					image = 'ok';
					text = 'Всё правильно :)';
				} else if(result == 'wrong_answer') {
					clazz = 'warning';
					image = 'error';
					text = 'Неверный ответ :(';
				} else {
					clazz = 'danger';
					image = 'error';
					text = 'Ошибка... :(';
				}

				test_rows[id].addClass(clazz);
				test_rows[id].find('.test_result').html('<img src="/static/images/test_' + image + '.png"><br>' + text);
			});
		});

		$('#example_tests tr').removeClass('success')
		                      .removeClass('warning')
		                      .removeClass('danger');

		$('#example_tests .test_result').hide();
	});

	$('#example_tests .debug_me').click(function() {
		var row = $(this).parent();

		visualizer.stdin = row.find('pre.input').text();
		visualizer.run();

		var visualizer_top = $("#visualizer").offset().top - 65;
		if($('body').scrollTop() > visualizer_top) {
			$('body').animate({scrollTop: visualizer_top}, 500);
		}
	});

	$('#example_tests .debug_me')[1].click();
})
