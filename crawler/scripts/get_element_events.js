
function getXPath (c) { if (c.id !== '') { return 'id(\"' + c.id + '\")' } if (c === document.body) { return c.tagName } var a = 0; var e = c.parentNode.childNodes; for (var b = 0; b < e.length; b++) { var d = e[b]; if (d === c) { return getXPath(c.parentNode) + '/' + c.tagName.toLowerCase() + '[' + (a + 1) + ']' } if (d.nodeType === 1 && d.tagName === c.tagName) { a++ } } };


function getListeners() {
    var EVENT_NAME_SYMBOL_REGX = /^__zone_symbol__(\w+)(true|false)$/;
    var elements = document.querySelectorAll("*");

    var listeners = [];

    for (const el of elements) {
        var xpath = getXPath(el);
        var events = ((el.eventListenerList != null) ? Object.keys(el.eventListenerList) : []);

        for (prop in el) {
            var match = EVENT_NAME_SYMBOL_REGX.exec(prop);
            var evtName = match && match[1];
            if (evtName) events.push(match[1]);
        }

        if (events.length > 0)
            listeners.push({"element": el, "xpath": xpath, "events": events});
    }

    return listeners;
}

return getListeners();

