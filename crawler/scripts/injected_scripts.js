(function () {

  function mAddEventListener (a, b, c) {
    this._addEventListener(a, b, c);
    if (!this.eventListenerList)
      this.eventListenerList = {};
    if (!this.eventListenerList[a])
      this.eventListenerList[a] = [];
    //this.removeEventListener(a,b,c); // TODO - handle duplicates..
    this.eventListenerList[a].push(b);
  };

  function mRemoveEventListener (a, b, c) {
    if (c == undefined)
      c = false;
    this._removeEventListener(a, b, c);
    if (!this.eventListenerList)
      this.eventListenerList = {};
    if (!this.eventListenerList[a])
      this.eventListenerList[a] = [];

    // Find the event in the list
    for (var i = 0; i < this.eventListenerList[a].length; i++) {
      if (this.eventListenerList[a][i].listener == b, this.eventListenerList[a][i].useCapture == c) { // Hmm..
        this.eventListenerList[a].splice(i, 1);
        break;
      }
    }
    if (this.eventListenerList[a].length == 0)
      delete this.eventListenerList[a];
  };

  function overrideEventListener (target) {
    if (!target || !target.prototype) {
      console.log("Target does not exist", target);
      return;
    }

    target.prototype._addEventListener = target.prototype.addEventListener;
    target.prototype.addEventListener = mAddEventListener;

//    target.prototype._removeEventListener = target.prototype.removeEventListener;
//    target.prototype.removeEventListener = mRemoveEventListener;
  }

  overrideEventListener(EventTarget);
  //overrideEventListener(Element);
  //overrideEventListener(Document);
  //overrideEventListener(window);


})();