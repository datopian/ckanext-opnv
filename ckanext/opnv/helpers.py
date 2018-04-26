import ckan.plugins.toolkit as toolkit

_ = toolkit._


def get_page_title():
    """Sets page title on site header image."""
    p = toolkit.request.urlvars.values()
    titles = {
        'package': _("Datasets"),
        'group': _("Groups"),
        'organization': _("Organizations"),
        'ckanext.showcase.controller:ShowcaseController': _("Showcases"),
        'about': _("About")
    }
    
    if p & titles.viewkeys():
        try:
            return titles[p[0]]
        except KeyError:
            return titles[p[1]]
    else:
        return None
