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

/**
 * Imgur Uploader
 * 
 * USAGE:
 * $('#imguruploader').imgurUploader({'clientid':'{{ imgur.client | safe }}',
 *                                  'target':'#image'})
 *                                  
 * 
 * 
 */

(function( $ ){

  $.fn.imgurUploader = function( options ) {  
    var settings = $.extend( {
      'clientid' : false,
      'target' : false,
    }, options);

    function open_file(context) {
    	context.data.find('input').click();
        return false;
    }
    
    function upload(context) {
        file = context.target.files[0];
        if (!file || !file.type.match(/image.*/)) return;

        var fd = new FormData();
        fd.append("image", file);
        fd.append("type", 'file');
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "https://api.imgur.com/3/image");
        xhr.setRequestHeader("Authorization", "Client-ID " + settings.clientid);
        xhr.onload = function() {
            var img_url = $.parseJSON(xhr.responseText).data.link;
            context.data.find('.thumbnail').css("background-image", "url('"+img_url+"')");
            context.data.find('.status').hide();
            $(settings.target).val(img_url)
        }
        context.data.find('.status').show();
        xhr.send(fd);
    }
    function empty(context) {
    	$(settings.target).val('');
    	context.data.find('.thumbnail').css("background-image", "");
    }
    
    return this.each(function() {
    	var $this = $(this);
        $this.find('a').first().click($this, open_file);
        $this.find('a').last().click($this, empty);
        $this.find('.thumbnail').css("background-image", "url('"+$(settings.target).val()+"')");
        $this.find('input').change($this, upload);
    });

  };
})( jQuery );