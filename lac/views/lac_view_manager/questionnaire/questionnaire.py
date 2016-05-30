# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

import deform
import colander
from pyramid.view import view_config

from dace.objectofcollaboration.principal.util import get_current
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.form import FormView
from pontus.schema import Schema, select
from pontus.widget import RadioChoiceWidget
from pontus.view import BasicView
from pontus.view_operation import MultipleView

from lac.views.widget import EmailInputWidget
from lac.content.processes.lac_view_manager.behaviors import (
    Questionnaire)
from lac.content.lac_application import CreationCulturelleApplication
from lac import _
from . import QUEST1


class QuestionnaireStudyReport(BasicView):
    title = 'Alert questionnaire'
    name = 'alertquestionnaire'
    template = 'lac:views/lac_view_manager/questionnaire/templates/questionnaire_info.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


def get_boolean_widget(**kwargs):
    @colander.deferred
    def boolean_widget(node, kw):
        request = node.bindings['request']
        localizer = request.localizer
        values = [('True', localizer.translate(_('Yes'))),
                  ('False', localizer.translate(_('No')))]
        return RadioChoiceWidget(
            values=values,
            template='lac:views/'
                     'templates/radio_choice.pt',
            inline=True,
            **kwargs)

    return boolean_widget


class Questionnaire1Schema(Schema):

    id = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        title="ID",
        default=QUEST1,
        missing=QUEST1
        )

    new_version = colander.SchemaNode(
        colander.String(),
        widget=get_boolean_widget(item_css_class="questionnaire-new-version"),
        title=_('Aimez-vous la nouvelle version ?'),
        missing='True',
        default='True'
    )

    explanation = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextAreaWidget(
            rows=3, cols=30,
            item_css_class="explanation-version hide-bloc"),
        title=_('Why no?'),
        missing=""
        )

    mobile_application = colander.SchemaNode(
        colander.String(),
        widget=get_boolean_widget(),
        title=_('Aimeriez-vous une application mobile ?'),
        missing='True',
        default='True'
    )

    email = colander.SchemaNode(
        colander.String(),
        widget=EmailInputWidget(),
        validator=colander.All(
            colander.Email(),
            colander.Length(max=100)
            ),
        title=_('Email')
        )


class QuestionnaireFormView(FormView):

    title = _('Votre avis')
    schema = select(Questionnaire1Schema(),
                    ['id', 'new_version', 'explanation',
                     'mobile_application', 'email'])
    behaviors = [Questionnaire]
    formid = 'formquestionnaire'
    name = 'questionnaireform'

    def before_update(self):
        user = get_current()
        if getattr(user, 'email', ''):
            self.schema.get('email').widget = deform.widget.HiddenWidget()

    def default_data(self):
        user = get_current()
        return {'email': getattr(user, 'email', '')}


@view_config(
    name='questionnaire',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class QuestionnaireView(MultipleView):
    title = _('Votre avis')
    name = 'questionnaire'
    viewid = 'questionnaire'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (QuestionnaireStudyReport, QuestionnaireFormView)
    validators = [Questionnaire.get_validator()]
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/questionnaire.js']}


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {Questionnaire: QuestionnaireView})
