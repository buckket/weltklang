$(function() {
    var loaded = false;
	$('#locale-button').click(function(){
		if (loaded) {
			return true;
		}
		loaded = true;
		$('#locale-placeholder').html('<i class="icon-spinner icon-spin"></i>');
		$('#locale-placeholder').load('/api/site/timezoneselector', function() {
			$('#timezone-image').timezonePicker({target:'#timezone-select'});
			update_pin();
			$('#lang').click(update_pin)
		});
		
	});
	$('#locale-placeholder').click(function(e){
		e.stopPropagation();
	});
	
	function update_pin() {
		$.getJSON('/api/site/localeinfo/'+$('#lang').val(), function(data) {
			$('.timezone-picker .timezone-pin').attr('src', data.img);
			});
	}
	
});