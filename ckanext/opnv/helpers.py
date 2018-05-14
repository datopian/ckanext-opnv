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


def org_list():
    return toolkit.get_action('organization_list')({}, {})


def get_org_dict(org):
    return toolkit.get_action('organization_show')({}, {'id': org})


def user_project_description(user):
    desc = None
    if user:
        desc = toolkit.get_action('user_extra_read')(
            {}, {'key': 'description', 'user_id': user['id']})
    return desc.get('value', None)
