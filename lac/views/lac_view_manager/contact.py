# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import deform
import colander
from pyramid.view import view_config

from dace.processinstance.core import (
    DEFAULTMAPPING_ACTIONS_VIEWS, Validator, ValidationError)
from dace.objectofcollaboration.entity import Entity
from pontus.form import FormView
from pontus.view import BasicView
from pontus.view_operation import MultipleView
from pontus.schema import Schema

from lac.content.processes.lac_view_manager.behaviors import (
    Contact)
from lac import _
from lac.utilities.utils import get_site_folder
from lac.views.widget import EmailInputWidget


@colander.deferred
def contact_choice(node, kw):
    site = get_site_folder(True)
    contacts = [c for c in getattr(site, 'contacts', [])
                if c.get('email', None)]
    values = [(c.get('email'), c.get('title')) for c in contacts]
    return deform.widget.CheckboxChoiceWidget(values=values)


class ContactSchema(Schema):

    services = colander.SchemaNode(
        colander.Set(),
        widget=contact_choice,
        title=_("Services to contact"),
        validator=colander.Length(min=1)
        )

    name = colander.SchemaNode(
        colander.String(),
        title=_('Name'),
        missing='',
        description=_('Please enter your full name')
        )

    email = colander.SchemaNode(
        colander.String(),
        widget=EmailInputWidget(),
        validator=colander.All(
            colander.Email(),
            colander.Length(max=100)
            ),
        title=_('Email'),
        description=_('Please enter your email address')
        )

    subject = colander.SchemaNode(
        colander.String(),
        title=_('Subject')
        )

    message = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextAreaWidget(rows=4, cols=60),
        title=_('Message'),
        description=_('Please enter the message you want to send.')
        )


class ContactStudyReport(BasicView):
    title = _('Services to contact')
    name = 'contactreport'
    template = 'lac:views/lac_view_manager/templates/contact.pt'

    def update(self):
        result = {}
        site = get_site_folder(True)
        values = {'contacts': getattr(site, 'contacts', [])}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class ContactValidator(Validator):

    @classmethod
    def validate(cls, context, request, **kw):
        site = get_site_folder(True)
        for contact in getattr(site, 'contacts', []):
            if contact.get('email', None):
                return True

        raise ValidationError()


class ContactForm(FormView):
    title = _('Contact')
    name = 'contactform'
    formid = 'formcontact'
    schema = ContactSchema()
    behaviors = [Contact]
    validators = [ContactValidator]
    validate_behaviors = False


@view_config(
    name='contact',
    context=Entity,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ContactMultipleView(MultipleView):
    title = _('Contact')
    name = 'contact'
    viewid = 'contact'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (ContactStudyReport, ContactForm)
    validators = [Contact.get_validator()]

    def before_update(self):
        if len(self.validated_children) == 1:
            self.validated_children[0].wrapper_template = 'daceui:templates/simple_view_wrapper.pt'

        super(ContactMultipleView, self).before_update()


DEFAULTMAPPING_ACTIONS_VIEWS.update({Contact: ContactMultipleView})
