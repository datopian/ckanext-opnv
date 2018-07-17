import re

import ckan.plugins.toolkit as toolkit
from ckan import model
from ckan.common import config
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
        title = p & titles.viewkeys()
        for t in title:
            return titles[t]
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
        if desc:
            return desc.get('value', None)


def is_mobile_device():
    MOBILE_AGENT_RE =\
        re.compile(r".*(iphone|ipad|mobile|androidtouch)", re.IGNORECASE)

    if MOBILE_AGENT_RE.match(toolkit.request.user_agent):
        return True

    return False


def get_googleanalytics_id():
    return config.get('googleanalytics.id')
