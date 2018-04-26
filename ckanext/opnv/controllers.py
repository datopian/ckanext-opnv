from ckan.lib import base
import ckan.plugins.toolkit as toolkit
render = base.render
BaseController = base.BaseController


class VrrController(BaseController):
    def impressum(self):
        return toolkit.render('impressum.html')

    def datenschutz(self):
        return toolkit.render('datenschutz.html')

    def kontakt(self):
        return toolkit.render('kontakt.html')

    def nutzungsvereinbarungen(self):
        return toolkit.render('nutzungsvereinbarungen.html')

    def netiquette(self):
        return toolkit.render('netiquette.html')
