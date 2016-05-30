# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import datetime
import colander
import deform
from zope.interface import implementer

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer
from substanced.interfaces import MODE_IMMEDIATE

from dace.objectofcollaboration.entity import Entity
from dace.descriptors import SharedUniqueProperty
from dace.util import getSite, find_catalog
from pontus.core import VisualisableElement, VisualisableElementSchema
from pontus.schema import select, omit
from pontus.widget import SimpleMappingWidget, TextInputWidget

from .interface import ISchedule
from lac.content.venue import OptionalVenueSchema, Venue
from lac import _
from lac.views.widget import DateIcalWidget
from lac.utilities.utils import dates
from lac.utilities.ical_date_utility import getMiseAJourSeance
from lac.core import dates_validator


def context_is_a_schedule(context, request):
    return request.registry.content.istype(context, 'schedule')


@colander.deferred
def ticket_type_choice(node, kw):
    root = getSite()
    values = [(str(i),  i) for i in root.ticket_types_values]
    return deform.widget.RadioChoiceWidget(
        values=values,
        item_css_class="schedule-ticket-type",
        multiple=False)


class ScheduleSchema(VisualisableElementSchema):
    """Schema for schedule"""

    name = NameSchemaNode(
        editing=context_is_a_schedule,
        )

    dates = colander.SchemaNode(
        colander.String(),
        validator=dates_validator,
        widget=DateIcalWidget(css_class="schedule-dates"),
        description=_('Indicate the dates and hours of the event.'),
        title=_('Dates'),
        )

    ticket_type = colander.SchemaNode(
        colander.String(),
        widget=ticket_type_choice,
        title=_('Ticket type'),
        )

    ticketing_url = colander.SchemaNode(
        colander.String(),
        widget=TextInputWidget(item_css_class="hide-bloc item-price"),
        title=_('Ticketing URL'),
        description=_('If you have an online ticketing service, you can enter the URL here.'),
        missing=''
        )

    price = colander.SchemaNode(
        colander.String(),
        default='0',
        widget=TextInputWidget(item_css_class="hide-bloc item-price"),
        title=_('Price'),
        )

    venue = omit(select(OptionalVenueSchema(editable=True,
                                    factory=Venue,
                                    omit=('id', ),
                                    name='venue',
                                    title=_('Venue'),
                                    oid='venue',
                                    widget=SimpleMappingWidget(
                                                 css_class="venue-block",
                                                 mapping_title=_("The venue of the event"))),
                        ['id', 'origin_oid', 'title', 'description',
                         'addresses', 'other_conf']),
                         #'kind', 'website','phone', 'capacity',
                 ['_csrf_token_', '__objectoid__'])


@content(
    'schedule',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(ISchedule)
class Schedule(VisualisableElement, Entity):
    """Schedule class"""

    name = renamer()
    cultural_event = SharedUniqueProperty("cultural_event", "schedules")
    venue = SharedUniqueProperty('venue', 'creations')
    dates = dates('dates')

    def __init__(self, **kwargs):
        super(Schedule, self).__init__(**kwargs)
        self.set_data(kwargs)
        self.state.append('created')

    @property
    def object_id(self):
        source_data = getattr(self, 'source_data', {})
        obj_id = source_data.get('id', '') + '_' +\
            source_data.get('source_id', '')
        if obj_id == '_':
            obj_id = str(getattr(self, '__oid__', None))+'_lac'

        return obj_id

    def reindex(self):
        if self.cultural_event:
            self.cultural_event.reindex()

        super(Schedule, self).reindex()

    def get_updated_dates(self, start_date=None, end_date=None):
        if start_date is None:
            start_date = datetime.datetime.now()

        return getMiseAJourSeance(
            self.dates, start_date, end_date, context=self)[0]

    def get_ticketing_url(self):
        if getattr(self, 'ticket_type', '') == 'Free admission':
            return ''

        return getattr(self, 'ticketing_url',
                       getattr(self.cultural_event, 'ticketing_url', None))

    def reindex_dates(self):
        catalog = find_catalog('lac')
        start = catalog['start_date']
        end = catalog['end_date']
        start.index_resource(self, action_mode=MODE_IMMEDIATE)
        end.index_resource(self, action_mode=MODE_IMMEDIATE)
