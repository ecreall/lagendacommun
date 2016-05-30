# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from dace.util import get_obj
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select, omit
from pontus.view import BasicView

from lac.content.processes.venue_management.behaviors import (
    ImproveVenue)
from lac.content.venue import (
    Venue)
from lac import _
from . import VenueSchema


@view_config(
    name='improvevenue',
    context=Venue,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ImproveVenueView(FormView):

    title = _('Improve the venue')
    schema = select(VenueSchema(factory=Venue,
                                editable=True,
                                omit=('metadata', )),
                    ['title', 'description', 'kind',
                     'capacity', 'handicapped_accessibility', 'addresses',
                     'contacts', ('metadata', ['object_labels', 'connections_to'])])
    behaviors = [ImproveVenue, Cancel]
    formid = 'formimprovevenue'
    name = 'improvevenue'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/addresse_management.js',
                                 'lac:static/js/contact_management.js']}

    def default_data(self):
        source = self.params('source')
        context = self.context
        if source:
            context = get_obj(int(source))

        result = context.get_data(omit(self.schema,
                                       ['_csrf_token_', '__objectoid__']))
        return result


@view_config(
    name='improvementofvenue',
    context=Venue,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ImprovementOfVenueView(BasicView):
    title = _('Consider as an improvement')
    name = 'improvementofvenue'
    behaviors = [ImproveVenue]

    def update(self):
        improvement_id = self.params('improvement')
        if improvement_id:
            try:
                improvement = get_obj(int(improvement_id))
                improvement.setproperty('original', self.context)
                improvement.reindex()
                self.context.reindex()
                return HTTPFound(self.request.resource_url(
                    improvement, "@@index"))
            except Exception:
                pass

        return HTTPFound(self.request.resource_url(
            self.context, "@@index"))


DEFAULTMAPPING_ACTIONS_VIEWS.update({ImproveVenue: ImproveVenueView})
