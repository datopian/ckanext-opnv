from ckan.lib.base import _

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
