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
    CreatePeriodicAdvertising)
from lac.content.periodic_advertising import (
    PeriodicAdvertisingSchema, PeriodicAdvertising)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _


@view_config(
    name='createperiodicadvertising',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreatePeriodicAdvertisingView(FormView):

    title = _('Create an advertisement in the periodical')
    schema = select(PeriodicAdvertisingSchema(factory=PeriodicAdvertising,
                                              editable=True),
                    ['title', 'visibility_dates',
                     'picture', 'format', 'position',
                     'request_quotation'])
    behaviors = [CreatePeriodicAdvertising, Cancel]
    formid = 'formcreateperiodicadvertising'
    name = 'createperiodicadvertising'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/periodic_advertising.js']}


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {CreatePeriodicAdvertising: CreatePeriodicAdvertisingView})
