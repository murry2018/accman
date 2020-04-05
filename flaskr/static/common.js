var onBodyLoad = function () {
    var tarea = document.querySelectorAll('textarea.autoexpand');
    var autoExpand = function (field) {
        field.style.height = 'inherit';
        var computed = window.getComputedStyle(field);
        var height = parseInt(computed.getPropertyValue('border-top-width'),10)
            + parseInt(computed.getPropertyValue('padding-top'), 10)
	    + field.scrollHeight
	    + parseInt(computed.getPropertyValue('padding-bottom'), 10)
	    + parseInt(computed.getPropertyValue('border-bottom-width'), 10);
        field.style.height = height + 'px';
    };
    if (tarea.length > 0) {
        for (var i = 0; i < tarea.length; i++) {
            tarea[i].addEventListener("input", function (event) {
                autoExpand(event.target);
            });
        }
    }
};
