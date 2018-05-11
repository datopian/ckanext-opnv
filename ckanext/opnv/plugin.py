import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.config.routing import SubMapper
from ckan.lib.plugins import DefaultTranslation


import ckanext.opnv.action
import ckanext.opnv.auth
from ckanext.opnv.model import setup as user_extra_model_setup
import ckanext.opnv.helpers as opnv_helpers


class OpnvPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IAuthFunctions, inherit=True)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITranslation)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'opnv')

    def configure(self, config):
        user_extra_model_setup()

    def before_map(self, map):
        user_ctrl = 'ckan.controllers.user:UserController'
        map.redirect('/user/register', '/user/login')
        with SubMapper(map, controller=user_ctrl) as m:
            m.connect('register', '/user/_register_partner', action='register')
        return map

    def get_auth_functions(self):
        auth_functions = {
            'user_extra_create': ckanext.opnv.auth.user_extra_create,
            'user_extra_update': ckanext.opnv.auth.user_extra_update,
            'user_extra_show': ckanext.opnv.auth.user_extra_show,

        }
        return auth_functions

    def get_actions(self):
        action_functions = {
            'package_show':
                ckanext.opnv.action.package_show,
        }
        return action_functions

    def get_helpers(self):
        helper_functions = {
            'get_page_title': opnv_helpers.get_page_title,
            'org_list': opnv_helpers.org_list,
            'get_org_dict': opnv_helpers.get_org_dict
        }
        return helper_functions

    def _modify_package_schema(self, schema):
        schema.update({
            'registered_only': [toolkit.get_validator('ignore_missing'),
                                toolkit.get_converter('convert_to_extras'), ]
        })
        return schema

    def show_package_schema(self):
        schema = super(OpnvPlugin, self).show_package_schema()
        schema.update({
            'registered_only': [toolkit.get_converter('convert_from_extras'),
                                toolkit.get_validator('ignore_missing')]
        })
        return schema

    def create_package_schema(self):
        schema = super(OpnvPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(OpnvPlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return ['dataset']
