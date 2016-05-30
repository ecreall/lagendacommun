# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select

from lac.content.processes.advertising_management.behaviors import (
    EditWebAdvertising)
from lac.content.web_advertising import (
    WebAdvertisingSchema, WebAdvertising)
from lac import _


@view_config(
    name='editwebadvertising',
    context=WebAdvertising,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditWebAdvertisingView(FormView):

    title = _('Edit the web advertisement')
    schema = select(WebAdvertisingSchema(factory=WebAdvertising,
                                         editable=True),
                    ['title', 'visibility_dates', 'tree',
                     'picture', 'html_content', 'advertisting_url',
                     'positions', 'request_quotation'])
    behaviors = [EditWebAdvertising, Cancel]
    formid = 'formeditwebadvertising'
    name = 'editwebadvertising'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/advertisting_management.js']}

    def default_data(self):
        return self.context

DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {EditWebAdvertising: EditWebAdvertisingView})
