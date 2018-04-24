from ckan.lib.navl.validators import (ignore_missing,
                                      not_empty,
                                      not_missing,
                                      ignore_empty
                                      )


def user_extra_schema():
    return {
        'user_id': [ignore_missing, unicode],
        'key': [not_empty, unicode],
        'value': [not_empty, unicode],
        'state': [ignore_missing, unicode]
    }


def user_extra_delete_schema():
    return {
        'key': [not_empty, unicode]
    }
