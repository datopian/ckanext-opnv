import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckanext.opnv.get


class OpnvPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'opnv')


class OpnvIDatasetFormPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IActions)

    def get_actions(self):
        action_functions = {
            'package_show':
                ckanext.opnv.get.package_show,
        }
        return action_functions

    def _modify_package_schema(self, schema):
        schema.update({
            'registered_only': [toolkit.get_validator('ignore_missing'),
                                toolkit.get_converter('convert_to_extras'), ]
        })
        return schema

    def show_package_schema(self):
        schema = super(OpnvIDatasetFormPlugin, self).show_package_schema()
        schema.update({
            'registered_only': [toolkit.get_converter('convert_from_extras'),
                                toolkit.get_validator('ignore_missing')]
        })
        return schema

    def create_package_schema(self):
        schema = super(OpnvIDatasetFormPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(OpnvIDatasetFormPlugin, self).update_package_schema()
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
