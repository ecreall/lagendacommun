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
    CreateWebAdvertising)
from lac.content.web_advertising import (
    WebAdvertisingSchema, WebAdvertising)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _


@view_config(
    name='createwebadvertising',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreateWebAdvertisingView(FormView):

    title = _('Create a web advertising')
    schema = select(WebAdvertisingSchema(factory=WebAdvertising,
                                         editable=True),
                    ['title', 'visibility_dates', 'tree',
                     'picture', 'html_content', 'advertisting_url',
                     'positions', 'request_quotation'])
    behaviors = [CreateWebAdvertising, Cancel]
    formid = 'formcreatewebadvertising'
    name = 'createwebadvertising'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/advertisting_management.js']}


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {CreateWebAdvertising: CreateWebAdvertisingView})
