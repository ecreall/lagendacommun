# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

import colander
import deform
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from substanced.interfaces import IUserLocator, IPasswordReset
from substanced.principal import DefaultUserLocator
from substanced.util import find_service

from dace.processinstance.core import Behavior
from pontus.form import FormView
from pontus.view_operation import MultipleView
from pontus.view import BasicView
from pontus.schema import Schema
from pontus.default_behavior import Cancel as DefaultCancel

from lac.utilities.utils import (
    get_site_folder)
from lac import _
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac.views.widget import EmailInputWidget
from lac.utilities.alerts_utility import alert


class Cancel(DefaultCancel):

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(request.root, ""))


class Send(Behavior):

    behavior_id = "send"
    title = _("Send")
    description = ""

    def start(self, context, request, appstruct, **kw):
        login = appstruct['email']
        adapter = request.registry.queryMultiAdapter(
            (context, request),
            IUserLocator
            )
        if adapter is None:
            adapter = DefaultUserLocator(context, request)

        user = adapter.get_user_by_email(login)
        if user is not None:
            principals = find_service(user, 'principals')
            reset = principals.add_reset(user)
            reseturl = request.resource_url(reset)
            email = user.email
            site = get_site_folder(True)
            localizer = request.localizer
            mail_template = site.get_mail_template('reset_password')
            subject = mail_template['subject']
            message = mail_template['template'].format(
                person=user,
                user_title=localizer.translate(
                    _(getattr(user, 'user_title', ''))),
                reseturl=reseturl,
                lac_title=request.root.title)
            alert('email', [site.get_site_sender()], [email],
                  {'subject': subject, 'body': message})

        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, ""))


@colander.deferred
def login_validator(node, kw):
    context = kw['context']
    request = kw['request']
    def _login_validator(node, value):
        adapter = request.registry.queryMultiAdapter(
            (context, request),
            IUserLocator
            )
        if adapter is None:
            adapter = DefaultUserLocator(context, request)

        user = adapter.get_user_by_email(value)
        if user is None:
            raise colander.Invalid(node, 'No such user %s' % value)

    return _login_validator


class ResetRequestSchema(Schema):
    """ The schema for validating password reset requests."""
    email = colander.SchemaNode(
        colander.String(),
        widget=EmailInputWidget(),
        validator=login_validator,
        title=_('Login (email)')
        )


class ResetRequestViewStudyReport(BasicView):
    title = _('Alert for reset')
    name = 'alertforreset'
    template = 'lac:views/user_management/templates/alert_reset.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class ResetRequestView(FormView):
    title = _('Request password reset')
    schema = ResetRequestSchema()
    behaviors = [Send, Cancel]


@view_config(
    name='resetpassword',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ResetRequestViewMultipleView(MultipleView):
    title = _('Request password reset')
    name = 'submitidea'
    viewid = 'submitidea'
    template = 'daceui:templates/mergedmultipleview.pt'
    views = (ResetRequestViewStudyReport, ResetRequestView)
    validators = [Send.get_validator()]


class Reset(Behavior):
    behavior_id = "send"
    title = _("Send")
    description = ""

    def start(self, context, request, appstruct, **kw):
        context.reset_password(appstruct['new_password'])
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(request.virtual_root, "@@login"))


class ResetSchema(Schema):
    """ The schema for validating password reset requests."""
    new_password = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=3, max=100),
        widget=deform.widget.CheckedPasswordWidget(),
        title=_("New Password")
        )


@view_config(
    name='',
    context=IPasswordReset,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ResetView(FormView):
    title = _('Reset Password')
    schema = ResetSchema()
    behaviors = [Reset, Cancel]
