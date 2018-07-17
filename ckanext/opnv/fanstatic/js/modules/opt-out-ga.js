var hasDismissed = window.localStorage.gaDismissed
var gaOptOut = $('.ga-opt-out.mobile')
var gaProperty = gaOptOut.attr('data-ga-id')
var disableStr = 'ga-disable-' + gaProperty;

if (document.cookie.indexOf(disableStr + '=true') > -1) {
  window[disableStr] = true;
}

if (!hasDismissed) {
    gaOptOut.show()

    gaOptOut.find('a').click(function() {
        window.localStorage.gaDismissed = true
        gaOptOut.hide()
        document.cookie = disableStr + '=true; expires=Thu, 31 Dec 2099 23:59:59 UTC; path=/';
        window[disableStr] = true;
    })
}
