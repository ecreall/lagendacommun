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
    Improve)
from lac.content.lac_application import CreationCulturelleApplication
from lac import _


class ImproveStudyReport(BasicView):
    title = 'Alert improve'
    name = 'alertimprove'
    template = 'lac:views/lac_view_manager/questionnaire/templates/improve_info.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class Improve1Schema(Schema):

    id = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        title="ID",
        missing="improve"
        )

    url = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        title="URL",
        missing="None"
        )

    improvement = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextAreaWidget(rows=3, cols=30),
        title=_('Vos suggestions')
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


class ImproveFormView(FormView):

    title = _('Votre avis')
    schema = select(Improve1Schema(),
                    ['id', 'url', 'improvement', 'email'])
    behaviors = [Improve]
    formid = 'formimprove'
    name = 'improveform'

    def before_update(self):
        user = get_current()
        if getattr(user, 'email', ''):
            self.schema.get('email').widget = deform.widget.HiddenWidget()

    def default_data(self):
        user = get_current()
        return {'email': getattr(user, 'email', '')}


@view_config(
    name='improve',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ImproveView(MultipleView):
    title = _('Votre avis')
    name = 'improve'
    viewid = 'improve'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (ImproveStudyReport, ImproveFormView)
    validators = [Improve.get_validator()]
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/questionnaire.js']}


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {Improve: ImproveView})
