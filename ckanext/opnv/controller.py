import logging

from ckan.controllers.user import UserController
import ckan.lib.base as base
import ckan.model as model
import ckan.lib.helpers as h
import ckan.authz as authz
import ckan.logic as logic
import ckan.lib.captcha as captcha
import ckan.lib.navl.dictization_functions as dictization_functions
from ckan.common import _, c, request, response
import ckan.plugins.toolkit as toolkit

log = logging.getLogger(__name__)


abort = base.abort
render = base.render

check_access = logic.check_access
get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
UsernamePasswordError = logic.UsernamePasswordError

DataError = dictization_functions.DataError
unflatten = dictization_functions.unflatten


log = logging.getLogger(__name__)


def set_repoze_user(user_id):
    '''Set the repoze.who cookie to match a given user_id'''
    if 'repoze.who.plugins' in request.environ:
        rememberer = request.environ['repoze.who.plugins']['friendlyform']
        identity = {'repoze.who.userid': user_id}
        response.headerlist += rememberer.remember(request.environ,
                                                   identity)


class OpnvUserController(UserController):

    def _save_new(self, context):
        try:
            data_dict = logic.clean_dict(unflatten(
                logic.tuplize_dict(logic.parse_params(request.params))))
            context['message'] = data_dict.get('log_message', '')
            captcha.check_recaptcha(request)
            user = get_action('user_create')(context, data_dict)
            user_extras = toolkit.get_action('user_extra_create')(context, data_dict)
        except NotAuthorized:
            abort(403, _('Unauthorized to create user %s') % '')
        except NotFound, e:
            abort(404, _('User not found'))
        except DataError:
            abort(400, _(u'Integrity Error'))
        except captcha.CaptchaError:
            error_msg = _(u'Bad Captcha. Please try again.')
            h.flash_error(error_msg)
            return self.new(data_dict)
        except ValidationError, e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.new(data_dict, errors, error_summary)
        if not c.user:
            # log the user in programatically
            set_repoze_user(data_dict['name'])
            h.redirect_to(controller='user', action='me')
        else:
            # #1799 User has managed to register whilst logged in - warn user
            # they are not re-logged in as new user.
            h.flash_success(_('User "%s" is now registered but you are still '
                              'logged in as "%s" from before') %
                            (data_dict['name'], c.user))
            if authz.is_sysadmin(c.user):
                # the sysadmin created a new user. We redirect him to the
                # activity page for the newly created user
                h.redirect_to(controller='user',
                              action='activity',
                              id=data_dict['name'])
            else:
                return render('user/logout_first.html')

    def register(self, data=None, errors=None, error_summary=None):
        context = {'model': model, 'session': model.Session, 'user': c.user,
                   'auth_user_obj': c.userobj}
        try:
            check_access('user_create', context)
        except NotAuthorized:
            abort(403, _('Unauthorized to register as a user.'))

        return self.new(data, errors, error_summary)

    def new(self, data=None, errors=None, error_summary=None):
        '''GET to display a form for registering a new user.
           or POST the form data to actually do the user registration.
        '''
        context = {'model': model,
                   'session': model.Session,
                   'user': c.user,
                   'auth_user_obj': c.userobj,
                   'schema': self._new_form_to_db_schema(),
                   'save': 'save' in request.params}
        try:
            check_access('user_create', context)
        except NotAuthorized:
            abort(403, _('Unauthorized to create a user'))

        if context['save'] and not data:
            return self._save_new(context)

        if c.user and not data and not authz.is_sysadmin(c.user):
            # #1799 Don't offer the registration form if already logged in
            return render('user/logout_first.html')

        data = data or {}
        errors = errors or {}
        error_summary = error_summary or {}

        vars = {'data': data, 'errors': errors, 'error_summary': error_summary}

        c.is_sysadmin = authz.is_sysadmin(c.user)
        c.form = render(self.new_user_form, extra_vars=vars)
        return render('user/new.html')
