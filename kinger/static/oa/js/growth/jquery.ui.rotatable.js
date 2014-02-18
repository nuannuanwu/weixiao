(function( $, undefined ) {
		
$.widget("ui.rotatable", $.ui.mouse, {
	
	options: {
		handle: false,
        angle: 0
	},
	
	handle: function(handle) {
		if (handle === undefined) {
			return this.options.handle;
		}
		this.options.handle = handle;
	},
    
    angle: function(angle) {
		if (angle === undefined) {
			return this.options.angle;
		}
		this.options.angle = angle;
        performRotation(this.element, this.options.angle);
    },
	
	_create: function() {
        var handle;
		if (!this.options.handle) {
			handle = $(document.createElement('div'));
    		handle.addClass('ui-rotatable-handle');
		}
        else {
            handle = this.options.handle;
        }
		handle.draggable({ helper: 'clone', start: dragStart });
		handle.on('mousedown', startRotate);
		handle.appendTo(this.element);
		degrees = getRotationDegrees(this.element)
		angle = degrees * (Math.PI/180);
		if (parseFloat(angle) > 0) {
			this.options.angle = angle;
		};
		this.element.data('angle', this.options.angle);
        performRotation(this.element, this.options.angle);
	}
});

var elementBeingRotated, mouseStartAngle, elementStartAngle;
$(document).on('mouseup', stopRotate);

function getElementCenter(el) {
	var elementOffset = getElementOffset(el);
	var elementCentreX = elementOffset.left + el.width() / 2;
	var elementCentreY = elementOffset.top + el.height() / 2;
	return Array(elementCentreX, elementCentreY);
};

function getElementOffset(el) {
	performRotation(el, 0);
	var offset = el.offset();
	performRotation(el, el.data('angle'));
	return offset;
};

// 2013-12-30
function getRotationDegrees(el) {
    var matrix = el.css("-webkit-transform") ||
    el.css("-moz-transform")    ||
    el.css("-ms-transform")     ||
    el.css("-o-transform")      ||
    el.css("transform");
    if(matrix !== 'none') {
        var values = matrix.split('(')[1].split(')')[0].split(',');
        var a = values[0];
        var b = values[1];
        var angle = Math.round(Math.atan2(b, a) * (180/Math.PI));
    } else { var angle = 0; }
    return (angle < 0) ? angle +=360 : angle;
};

function performRotation(el, radians) {
	// el.css('transform','rotate(' + angle + 'rad)');
	// el.css('-moz-transform','rotate(' + angle + 'rad)');
	// el.css('-webkit-transform','rotate(' + angle + 'rad)');
	// el.css('-o-transform','rotate(' + angle + 'rad)');
	angle = radians * (180/Math.PI)
	el.css('transform','rotate(' + angle + 'deg)');
	el.css('-moz-transform','rotate(' + angle + 'deg)');
	el.css('-webkit-transform','rotate(' + angle + 'deg)');
	el.css('-o-transform','rotate(' + angle + 'deg)');
};

function dragStart(event) {
	if (elementBeingRotated) return false;
};

function rotateElement(event) {
	if (!elementBeingRotated) return false;

	var center = getElementCenter(elementBeingRotated);
	var xFromCenter = event.pageX - center[0];
	var yFromCenter = event.pageY - center[1];
	var mouseAngle = Math.atan2(yFromCenter, xFromCenter);
	var rotateAngle = mouseAngle - mouseStartAngle + elementStartAngle;
	
	performRotation(elementBeingRotated, rotateAngle);
	elementBeingRotated.data('angle', rotateAngle);
	
	return false;
};

function startRotate(event) {
	elementBeingRotated = $(this).parent(); 
	var center = getElementCenter(elementBeingRotated);
	var startXFromCenter = event.pageX - center[0];
	var startYFromCenter = event.pageY - center[1];
	mouseStartAngle = Math.atan2(startYFromCenter, startXFromCenter);
	elementStartAngle = elementBeingRotated.data('angle');

	$(document).on('mousemove', rotateElement);
	
	return false;
};

function stopRotate(event) {
	if (!elementBeingRotated) return;
	$(document).unbind('mousemove');
	setTimeout( function() { elementBeingRotated = false; }, 10 );
	return false;
};

})(jQuery);