# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi
# TODO: finish to clean, use our own templates, ... ?

from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPFound
    )
from pyramid.renderers import get_renderer
from pyramid.session import check_csrf_token
from pyramid.security import remember

from velruse import login_url as velruse_login_url
from substanced.util import get_oid

from substanced.event import LoggedIn

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView, ViewError

from lac import _
from lac.content.processes.user_management.behaviors import (
    LogIn, create_user)
from lac.content.lac_application import (
    CreationCulturelleApplication)


@view_config(
    name='login',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class LoginView(BasicView):
    title = _('Log in')
    name = 'login'
    behaviors = [LogIn]
    template = 'lac:views/user_management/templates/login.pt'
    wrapper_template = 'daceui:templates/simple_view_wrapper.pt'
    viewid = 'login'
    isexecutable = True

    def update(self):
        request = self.request
        login_url = request.resource_url(request.context, 'login')
        login_url2 = request.resource_url(request.context, '@@login')
        referrer = request.path_url
        if '/auditstream-sse' in referrer:
            # If we're being invoked as the result of a failed request to the
            # auditstream sse view, bail.  Otherwise the came_from will be set to
            # the auditstream URL, and the user who this happens to will eventually
            # be redirected to it and they'll be left scratching their head when
            # they see e.g. "id: 0-10\ndata: " when they log in successfully.
            return HTTPForbidden()

        if login_url in referrer or login_url2 in referrer:
            # never use the login form itself as came_from
            referrer = request.resource_url(request.virtual_root)

        came_from = request.session.setdefault(
            'lac.came_from', referrer).replace('@@dace-ui-api-view', '@@index')
        login = ''
        password = ''
        message = None
        messages = {}
        if 'login_form.submitted' in request.params:
            try:
                check_csrf_token(request)
            except:
                request.sdiapi.flash(_('Failed login (CSRF)'), 'danger')
            else:
                login = request.params['email']
                password = request.params['password']
                result = self.execute(dict(
                    login=login,
                    password=password,
                    came_from=came_from
                    ))
                if result[0].get('logged', False):
                    return result[0].get('redirect')

                error = ViewError()
                error.principalmessage = _("Failed login")
                message = error.render_message(request)
                messages.update({error.type: [message]})
                self.finished_successfully = False

        # Pass this through FBO views (e.g., forbidden) which use its macros.
        template = get_renderer(
            'lac:views/user_management/templates/login.pt').implementation()
        site = self.request.get_site_folder
        values = dict(
            velruse_login_url=velruse_login_url,
            applications=getattr(site, 'applications', []),
            url=request.resource_url(request.virtual_root, ''),
            came_from=came_from,
            login=login,
            password=password,
            login_template=template,
            form_id=self.viewid,
            check_url=self.request.resource_url(
                self.request.root, '@@creationculturelapi',
                query={'op': 'check_user'})
            )
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        item['messages'] = messages
        result = {}
        result['coordinates'] = {self.coordinates: [item]}
        return result


@view_config(
    context='velruse.AuthenticationComplete',
    renderer='pontus:templates/views_templates/grid.pt',
    )
class LoginCompleteView(BasicView):
    title = _('Login complete')
    template = 'lac:views/user_management/templates/result.pt'
    wrapper_template = 'daceui:templates/simple_view_wrapper.pt'
    viewid = 'login_complete'

    def update(self):
        values = {
            'profile': self.context.profile,
            'credentials': self.context.credentials,
            'external_login': True
        }
        self.request.root = self.request.sdiapi.get_connection(
            self.request).root().get('app_root')
        self.request.virtual_root = self.request.root
        self.request.context = self.request.root
        self.context = self.request.root
        result = create_user(self.context, self.request, values)
        person = result.get('user', None)
        if person:
            headers = remember(self.request, get_oid(person))
            self.request.registry.notify(
                LoggedIn(getattr(person, 'email', ''), person,
                         self.context, self.request))
            return HTTPFound(location=self.request.resource_url(self.context),
                             headers=headers)

        root = self.request.root
        return HTTPFound(self.request.resource_url(root))


@view_config(
    context='velruse.AuthenticationDenied',
    renderer='pontus:templates/views_templates/grid.pt',
    )
class LoginDeniedView(BasicView):
    title = _('Login denied')
    name = 'login_denied'
    template = 'lac:views/user_management/templates/result.pt'
    wrapper_template = 'daceui:templates/simple_view_wrapper.pt'
    viewid = 'login_denied'

    def update(self):
        self.request.root = self.request.sdiapi.get_connection(
            self.request).root().get('app_root')
        self.request.virtual_root = self.request.root
        self.request.context = self.request.root
        self.context = self.request.root
        values = {
            'result': 'denied',
        }
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result = {}
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update({LogIn: LoginView})
