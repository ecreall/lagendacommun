# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.view import BasicView
from pontus.schema import select

from lac.views.widget import TOUCheckboxWidget
from lac.content.processes.user_management.behaviors import (
    Registration)
from lac.content.person import PersonSchema, Preregistration
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _


@colander.deferred
def conditions_widget(node, kw):
    request = node.bindings['request']
    terms_of_use = request.get_site_folder['terms_of_use']
    return TOUCheckboxWidget(tou_file=terms_of_use)


class RegistrationSchema(PersonSchema):

    accept_conditions = colander.SchemaNode(
        colander.Boolean(),
        widget=conditions_widget,
        label=_('I have read and accept the terms and conditions.'),
        title='',
        missing=False
    )


@view_config(
    name='registration',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RegistrationView(FormView):

    title = _('Your registration')
    schema = select(RegistrationSchema(factory=Preregistration,
                                       editable=True,
                                       omit=('structures',)),
                    ['user_title',
                     'first_name',
                     'last_name',
                     'email',
                     'is_cultural_animator',
                     'structures',
                     'accept_conditions'])
    behaviors = [Registration, Cancel]
    formid = 'formregistration'
    name = 'registration'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/addresse_management.js',
                                 'lac:static/js/user_management.js']}


@view_config(
    name='registrationsubmitted',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RegistrationSubmittedView(BasicView):
    template = 'lac:views/user_management/templates/registrationsubmitted.pt'
    title = _('Please confirm your registration ')
    name = 'registrationsubmitted'
    viewid = 'deactivateview'

    def update(self):
        result = {}
        body = self.content(args={}, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update({Registration: RegistrationView})
