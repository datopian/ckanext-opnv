import logging
import json
import socket
from pprint import pprint

from paste.deploy.converters import asbool

import ckan.lib.dictization
import ckan.logic as logic
import ckan.logic.action
import ckan.logic.schema
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.lib.navl.dictization_functions
import ckan.plugins as plugins
import ckan.lib.search as search
import ckan.lib.plugins as lib_plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.navl.dictization_functions as df
from ckanext.opnv.model import UserExtra
from ckanext.opnv.user_schema import user_extra_schema
from ckanext.opnv.user_schema import user_extra_delete_schema
from pylons import c

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
_validate = ckan.lib.navl.dictization_functions.validate
_table_dictize = ckan.lib.dictization.table_dictize
_check_access = logic.check_access
NotFound = logic.NotFound
ValidationError = logic.ValidationError
_get_or_bust = logic.get_or_bust


log = logging.getLogger(__name__)


def user_extra_create(context, data_dict):
    '''Create user extra parameter.

        :param key: Key of the parameter.
        :type key: string

        :param value: Value of the parameter.
        :type value: string

        :param active: State of the parameter. Default is active.
        :type active: string

        '''

    logic.check_access('user_extra', context, data_dict)
    data, errors = df.validate(data_dict, user_extra_schema(), context)

    if errors:
        raise toolkit.ValidationError(errors)

    model = context.get('model')
    user = context.get('user')
    user_obj = model.User.get(user)

    user_id = user_obj.id
    key = data.get('key')
    value = data.get('value')
    state = data.get('state', 'active')

    user_extra = UserExtra.get(user_id, key)
    if user_extra:
        user_extra.key = key
        user_extra.value = value
        user_extra.save()
    else:
        user_extra = UserExtra(
            user_id=user_id,
            key=key,
            value=value,
            state=state
        )
        user_extra.save()

    return _table_dictize(user_extra, context)


def user_extra_read(context, data_dict):
    '''Read user extra parameter.

        :param key: Key of the parameter.
        :type key: string

        '''

    logic.check_access('user_extra', context, data_dict)
    data, errors = df.validate(data_dict, user_extra_delete_schema(), context)

    if errors:
        raise toolkit.ValidationError(errors)

    model = context.get('model')
    user = context.get('user')
    user_obj = model.User.get(user)

    user_id = user_obj.id
    key = data.get('key')

    user_extra = UserExtra.get(user_id, key)
    if user_extra is None:
        return user_extra

    return _table_dictize(user_extra, context)


def user_extra_update(context, data_dict):
    '''Update user extra parameter.

        :param key: Key of the parameter you want to update.
        :type key: string

        :param value: The new value of the parameter.
        :type value: string

        '''

    logic.check_access('user_extra', context, data_dict)
    data, errors = df.validate(data_dict, user_extra_schema(), context)

    if errors:
        raise toolkit.ValidationError(errors)

    model = context.get('model')
    user = context.get('user')
    user_obj = model.User.get(user)
    user_id = user_obj.id
    key = data.get('key')
    value = data.get('value')

    user_extra = UserExtra.get(user_id, key)
    if user_extra is None:
        raise logic.NotFound

    user_extra.key = key
    user_extra.value = value
    user_extra.save()

    return _table_dictize(user_extra, context)


def user_extra_delete(context, data_dict):
    '''Delete user extra parameter.

        :param key: Key of the parameter you want to delete.
        :type key: string

        '''

    logic.check_access('user_extra', context, data_dict)
    data, errors = df.validate(data_dict, user_extra_delete_schema(), context)

    if errors:
        raise toolkit.ValidationError(errors)

    model = context.get('model')
    user = context.get('user')
    user_obj = model.User.get(user)
    user_id = user_obj.id
    key = data.get('key')

    UserExtra.delete(user_id, key)

    return {
        'message': 'Extra with key: %s, deleted' % key
    }


def _add_tracking_summary_to_resource_dict(resource_dict, model):
    '''Add page-view tracking summary data to the given resource dict.

    '''
    tracking_summary = model.TrackingSummary.get_for_resource(
        resource_dict['url'])
    resource_dict['tracking_summary'] = tracking_summary


def package_show(context, data_dict):
    '''Return the metadata of a dataset (package) and its resources.

    :param id: the id or name of the dataset
    :type id: string
    :param use_default_schema: use default package schema instead of
        a custom schema defined with an IDatasetForm plugin (default: False)
    :type use_default_schema: bool
    :param include_tracking: add tracking information to dataset and
        resources (default: False)
    :type include_tracking: bool
    :rtype: dictionary

    '''
    model = context['model']
    context['session'] = model.Session
    name_or_id = data_dict.get("id") or _get_or_bust(data_dict, 'name_or_id')

    pkg = model.Package.get(name_or_id)

    if pkg is None:
        raise NotFound

    context['package'] = pkg

    _check_access('package_show', context, data_dict)

    if data_dict.get('use_default_schema', False):
        context['schema'] = ckan.logic.schema.default_show_package_schema()
    include_tracking = asbool(data_dict.get('include_tracking', False))

    package_dict = None
    use_cache = (context.get('use_cache', True)
                 and not 'revision_id' in context
                 and not 'revision_date' in context)
    if use_cache:
        try:
            search_result = search.show(name_or_id)
        except (search.SearchError, socket.error):
            pass
        else:
            use_validated_cache = 'schema' not in context
            if use_validated_cache and 'validated_data_dict' in search_result:
                package_json = search_result['validated_data_dict']
                package_dict = json.loads(package_json)
                package_dict_validated = True
            else:
                package_dict = json.loads(search_result['data_dict'])
                package_dict_validated = False
            metadata_modified = pkg.metadata_modified.isoformat()
            search_metadata_modified = search_result['metadata_modified']
            # solr stores less precice datetime,
            # truncate to 22 charactors to get good enough match
            if metadata_modified[:22] != search_metadata_modified[:22]:
                package_dict = None

    if not package_dict:
        package_dict = model_dictize.package_dictize(pkg, context)
        package_dict_validated = False

    if include_tracking:
        # page-view tracking summary data
        package_dict['tracking_summary'] = (
            model.TrackingSummary.get_for_package(package_dict['id']))

        for resource_dict in package_dict['resources']:
            _add_tracking_summary_to_resource_dict(resource_dict, model)

    if context.get('for_view'):
        for item in plugins.PluginImplementations(plugins.IPackageController):
            package_dict = item.before_view(package_dict)

    for item in plugins.PluginImplementations(plugins.IPackageController):
        item.read(pkg)

    for item in plugins.PluginImplementations(plugins.IResourceController):
        for resource_dict in package_dict['resources']:
            item.before_show(resource_dict)

    if not package_dict_validated:
        package_plugin = lib_plugins.lookup_package_plugin(
            package_dict['type'])
        if 'schema' in context:
            schema = context['schema']
        else:
            schema = package_plugin.show_package_schema()
        if schema and context.get('validate', True):
            package_dict, errors = lib_plugins.plugin_validate(
                package_plugin, context, package_dict, schema,
                'package_show')

    for item in plugins.PluginImplementations(plugins.IPackageController):
        item.after_show(context, package_dict)

    return package_dict
