ckan.module('opnv-dismiss-ga-message', function($) {
    return {
        initialize: function() {
            var hasDismissed = window.localStorage.gaDismissed
            var gaOptOut = $('.ga-opt-out')

            if (!hasDismissed) {
                gaOptOut.show()
            }

            this.el.on('click', function() {
                window.localStorage.gaDismissed = true
                gaOptOut.hide()
            })
        }
    }
})
