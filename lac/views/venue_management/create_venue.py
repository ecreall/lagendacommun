# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select

from lac.content.processes.venue_management.behaviors import (
    CreateVenue)
from lac.content.venue import (
     Venue)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _
from . import VenueSchema


@view_config(
    name='createvenue',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class CreateVenueView(FormView):

    title = _('Create a venue')
    schema = select(VenueSchema(factory=Venue,
                                editable=True,
                                omit=('metadata', )),
               ['title', 'description', 'kind',
                'capacity', 'handicapped_accessibility', 'addresses',
                'contacts', ('metadata', ['object_labels', 'connections_to'])])
    behaviors = [CreateVenue, Cancel]
    formid = 'formcreatevenue'
    name = 'createvenue'
    requirements = {'css_links':[],
                    'js_links':['lac:static/js/addresse_management.js',
                                'lac:static/js/contact_management.js']}



DEFAULTMAPPING_ACTIONS_VIEWS.update({CreateVenue: CreateVenueView})