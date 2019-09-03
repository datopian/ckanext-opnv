from ckan.lib.base import _
from ckan.logic.auth.get import user_list
import ckan.plugins.toolkit as toolkit

import logging

log = logging.getLogger(__name__)


def _user_own_data(context, data_dict):
    user_obj = context.get('auth_user_obj') or context.get('user_obj')
    if user_obj and user_obj.id == data_dict.get('user_id', ''):
        return {'success': True}
    else:
        return {'success': False,
                'msg': _('Not authorized to perform this request')}


def user_extra_create(context, data_dict):
    """User accesses only his own data."""
    return _user_own_data(context, data_dict)


def user_extra_update(context, data_dict):
    """User accesses only his own data."""
    return _user_own_data(context, data_dict)


def user_extra_show(context, data_dict):
    """User accesses only his own data."""
    return _user_own_data(context, data_dict)

def opnv_user_list(context, data_dict):
    is_sysadmin = toolkit.check_access('sysadmin', context, data_dict)
    if context.get('ignore_auth') or is_sysadmin:
        return {'success': True}

    if user:
        user_teams = toolkit.get_action('organization_list_for_user')(
            {'ignore_auth': True}, {'id': user})
        is_org_admin = any([t.get('capacity') == 'admin' for t in user_teams])
        return {'success': is_org_admin}

    return user_list(context, data_dict)
