function check_username(element) {
	var regexp = new RegExp('^[0-9a-z_-]*$', 'i')
	if (!regexp.test($(element).val())) {
		element.setCustomValidity('Username contains invalid characters');
		$.pnotify({
	        text: 'Your username contains invalid chars<br> only [0-9a-z_-] allowed'
	    });
		return
	}
	$.ajax({
		  url: '/register/check',
		  type: 'POST',
		  dataType: 'json',
		  data: {'username':$(element).val()},
		  success: function(data) {
			  if (data.username == 'taken') {
				  element.setCustomValidity('Username already taken');
				  $.pnotify({
				        text: 'Your username is already taken :( '
				    });
			  } else {
				  element.setCustomValidity('');
			  }
		  }
		});
}

function check_password() {
	var pass = $('#reg_password')
	var ret = $('#reg_password_conf')
	if (pass.val().length < 3) {
		pass[0].setCustomValidity('password too short')
		$.pnotify({
	        text: 'Your password is too short'
	    });
	} else if (pass.val() != ret.val() && ret.val() != '') {
		pass[0].setCustomValidity('passwords don\'t match')
		ret[0].setCustomValidity('passwords don\'t match')
		$.pnotify({
	        text: 'Your password don\'t match'
	    });
	} else {
		pass[0].setCustomValidity('')
		ret[0].setCustomValidity('')
	}
}

function check_stream_password() {
	var pass = $('#reg_stream_password')
	var ret = $('#reg_stream_password_conf')
	if (pass.val().length < 3) {
		pass[0].setCustomValidity('password too short')
		$.pnotify({
	        text: 'Your password is too short'
	    });
	} else if (pass.val() != ret.val() && ret.val() != '') {
		pass[0].setCustomValidity('passwords don\'t match')
		ret[0].setCustomValidity('passwords don\'t match')
		$.pnotify({
	        text: 'Your password don\'t match'
	    });
	} else {
		pass[0].setCustomValidity('')
		ret[0].setCustomValidity('')
	}
}

function submit_form(button) {
	$(button).attr("disabled", true);
	$(button).val("Please wait...")
	$.ajax({
		  url: '/register/finish',
		  type: 'POST',
		  dataType: 'json',
		  data: {'username':$('#reg_username').val(),
			     'password':$('#reg_password').val(),
			     'stream_password':$('#reg_stream_password').val()},
		  success: function(data) {
			  if(!data.success) {
				  if (data.username == 'taken') {
					  $('#reg_username')[0].setCustomValidity('Username already taken');
					  $.pnotify({
					        text: 'Your username is already taken :( '
					  });
				  } else if (data.username == 'invalid') {
					  $('#reg_username')[0].setCustomValidity('Username contains invalid characters');
						$.pnotify({
					        text: 'Your username contains invalid chars<br> only [0-9a-z_-] allowed'
					    });
				  }
				  if (data.password == 'invalid') {
					  $('#reg_password')[0].setCustomValidity('password too short')
						$.pnotify({
					        text: 'Your password is too short'
					    });
				  }
				  if (data.stream_password == 'invalid') {
					  $('#reg_stream_password')[0].setCustomValidity('password too short')
						$.pnotify({
					        text: 'Your password is too short'
					    });
				  }
			   $(button).removeAttr("disabled");
			   $(button).val("Register")
			  } else {
				  window.location.replace("/register/success");
			  }
		  }
		})
	return false
}