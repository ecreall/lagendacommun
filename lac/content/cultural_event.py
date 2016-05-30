# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
import deform
import datetime
import pytz
from zope.interface import implementer, invariant

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer, get_oid
from substanced.property import PropertySheet

from dace.util import getSite
from dace.descriptors import (
    SharedMultipleProperty,
    CompositeUniqueProperty,
    SharedUniqueProperty)
from pontus.core import (
    VisualisableElement,
    VisualisableElementSchema,
    )
from pontus.file import ObjectData
from pontus.schema import select, omit
from pontus.widget import (
    ImageWidget,
    SimpleMappingWidget,
    SequenceWidget)
from pontus.form import FileUploadTempStore
from deform_treepy.widget import (
    DictSchemaType)

from lac.views.widget import TOUCheckboxWidget
from lac import _
from lac.content.schedule import ScheduleSchema, Schedule
from lac.content.interface import ICulturalEvent
from lac.content.artist import (
    ArtistInformationSheetSchema,
    ArtistInformationSheet)
from lac.views.widget import (
    LimitedTextAreaWidget)
from lac.core import (
    DuplicableEntity,
    SearchableEntity,
    SearchableEntitySchema,
    keywords_validator,
    keyword_widget,
    ParticipativeEntity)
from lac.core_schema import artists_choice, ContactSchema
from lac.file import Image
from lac.content.keyword import DEFAULT_TREE
from lac.utilities.ical_date_utility import occurences_start
from lac.utilities.utils import to_localized_time
from lac.views.widget import RichTextWidget, SimpleSequenceWidget
from lac.utilities.duplicates_utility import (
    find_duplicates_cultural_events)


def context_is_a_cultural_event(context, request):
    return request.registry.content.istype(context, 'cultural_event')


@colander.deferred
def picture_widget(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    tmpstore = FileUploadTempStore(request)
    source = None
    root = getSite()
    if context is not root:
        if context.picture:
            source = context.picture

    return ImageWidget(
        tmpstore=tmpstore,
        max_height=200,
        max_width=400,
        source=source,
        selection_message=_("Upload image.")
        )


@colander.deferred
def conditions_widget(node, kw):
    request = node.bindings['request']
    terms_of_use = request.get_site_folder['terms_of_use']
    return TOUCheckboxWidget(tou_file=terms_of_use)


class CulturalEventSchema(VisualisableElementSchema, SearchableEntitySchema):
    """Schema for cultural event"""

    name = NameSchemaNode(
        editing=context_is_a_cultural_event,
        )

    title = colander.SchemaNode(
        colander.String(),
        title=_('Title'),
        description=_('Enter a title for your announcement.')
        )

    description = colander.SchemaNode(
        colander.String(),
        widget=LimitedTextAreaWidget(rows=5,
                                     cols=30,
                                     limit=350,
                                     alert_values={'limit': 350},
                                     css_class="ce-field-description"),
        title=_("Brief description"),
        description=_('Describe succinctly the event.'),
        )

    details = colander.SchemaNode(
        colander.String(),
        widget=RichTextWidget(css_class="ce-field-details"),
        missing="",
        description=_('You can describe in detail the event. (Recommended)'),
        title=_('Details'),
        oid='detailed_description'
        )

    artists_ids = colander.SchemaNode(
        colander.Set(),
        widget=artists_choice,
        title=_('Artists'),
        description=_('You can enter the artists names.'),
        missing=[]
        )

    artists = colander.SchemaNode(
        colander.Sequence(),
        omit(select(ArtistInformationSheetSchema(editable=True,
                                                 factory=ArtistInformationSheet,
                                                 omit=('id', ),
                            widget=SimpleMappingWidget(
                                  css_class='artist-data object-well'
                                            ' default-well'),
                                  name=_('artist')),
                   ['id', 'origin_oid', 'title',
                    'description', 'picture', 'biography', 'is_director']),
            ['_csrf_token_', '__objectoid__']),
        widget=SequenceWidget(css_class='artists-values',
                            template='lac:views/'
                                     'templates/sequence_modal.pt',
                            item_template='lac:views/'
                                          'templates/sequence_modal_item.pt'),
        title=_('Artists'),
        )

    tree = colander.SchemaNode(
        typ=DictSchemaType(),
        validator=colander.All(keywords_validator),
        widget=keyword_widget,
        default=DEFAULT_TREE,
        title=_('Categories'),
        description=_('Indicate the category of the event. Please specify a second keyword level for each category chosen.')
        )

    contacts = colander.SchemaNode(
        colander.Sequence(),
        omit(select(ContactSchema(name='contact',
                                  widget=SimpleMappingWidget(
                                  css_class='contact-well object-well default-well')),
                    ['phone', 'surtax', 'email', 'website', 'fax']),
            ['_csrf_token_']),
        widget=SimpleSequenceWidget(
            add_subitem_text_template=_('Add a new contact'),
            remove_subitem_text_template=_('Remove the contact')
            ),
        title=_('Contacts'),
        description=_('Indicate contacts of the event. If none is specified, venues contacts will be assigned to the event.'),
        oid='contacts'
        )

    picture = colander.SchemaNode(
        ObjectData(Image), #Pontus
        widget=picture_widget,
        title=_('Picture'),
        description=_('You can choose a picture to illustrate your announcement.'),
        missing=None,
        )

    schedules = colander.SchemaNode(
        colander.Sequence(),
        omit(select(ScheduleSchema(
                        name='schedule',
                        factory=Schedule,
                        editable=True,
                        widget=SimpleMappingWidget(
                            css_class='schedule-well object-well default-well'),
                        omit=('venue', )),
                    ['dates', 'venue', 'ticket_type', 'price', 'ticketing_url']),
            ['_csrf_token_']),
        widget=SimpleSequenceWidget(
            min_len=1,
            add_subitem_text_template=_('Add a new schedule'),
            remove_subitem_text_template=_('Remove the schedule')),
        description=_('If the event takes place in several locations, add a session by clicking the plus sign on the bottom right of the block "sessions".'),
        title=_('Schedules'),
        )

    selling_tickets = colander.SchemaNode(
        colander.Boolean(),
        widget=deform.widget.CheckboxWidget(),
        label=_('Selling tickets'),
        title='',
        description=_('Check this box if you want to be accompanied or to receive information on selling tickets online.'),
        default=False,
        missing=False
        )

    ticketing_url = colander.SchemaNode(
        colander.String(),
        title=_('Ticketing URL'),
        description=_('For the online ticket sales.'),
        missing=None
        )

    accept_conditions = colander.SchemaNode(
        colander.Boolean(),
        widget=conditions_widget,
        label=_('I have read and accept the terms and conditions'),
        title='',
        missing=False
    )

    @invariant
    def contacts_invariant(self, appstruct):
        if not appstruct['contacts'] and \
           any(not s['venue']['other_conf']['contacts']
               for s in appstruct['schedules']):
            raise colander.Invalid(
                self.get('contacts'),
                _("Event's contact or all venues's contacts must be defined."))


class CulturalEventPropertySheet(PropertySheet):
    schema = select(CulturalEventSchema(), ['name'])


@content(
    'cultural_event',
    icon='glyphicon glyphicon-align-left',
    propertysheets=(
        ('Basic', CulturalEventPropertySheet),
        )
    )
@implementer(ICulturalEvent)
class CulturalEvent(VisualisableElement, DuplicableEntity,
                    ParticipativeEntity, SearchableEntity):
    """Cultural_event class"""

    type_title = _('Cultural event')
    icon = 'lac-icon icon-bullhorn'
    templates = {'default': 'lac:views/templates/culturalevent_result.pt',
                 'bloc': 'lac:views/templates/culturalevent_result.pt',
                 'diff': 'lac:views/templates/diff_event_template.pt',
                 'extraction': 'lac:views/templates/extraction/culturalevent_result.pt',
                 'duplicates': 'lac:views/templates/culturalevent_duplicates.pt',
                 'map': 'lac:views/templates/map/cultural_event.pt'}
    name = renamer()
    schedules = SharedMultipleProperty("schedules", "cultural_event")
    picture = CompositeUniqueProperty('picture')
    artists = SharedMultipleProperty('artists', 'creations')
    author = SharedUniqueProperty('author', 'contents')

    def __init__(self, **kwargs):
        super(CulturalEvent, self).__init__(**kwargs)
        self.set_data(kwargs)

    @property
    def object_id(self):
        source_data = getattr(self, 'source_data', {})
        obj_id = str(source_data.get('id', getattr(self, '__oid__', None)))
        obj_id += '_' + source_data.get('source_id', 'lac')
        return obj_id

    @property
    def dates_end_date(self):
        if not self.schedules:
            return datetime.datetime.combine(datetime.datetime.now(),
                                 datetime.time(0, 0, 0, tzinfo=pytz.UTC))

        return max([getattr(schedule, 'dates_end_date', None)
                    for schedule in self.schedules if
                    getattr(schedule, 'dates_end_date', None)])

    @property
    def dates_start_date(self):
        if not self.schedules:
            return datetime.datetime.combine(datetime.datetime.now(),
                                datetime.time(0, 0, 0, tzinfo=pytz.UTC))

        return min([getattr(schedule, 'dates_start_date', None)
                    for schedule in self.schedules if
                    getattr(schedule, 'dates_start_date', None)])

    @property
    def dates_recurrence(self):
        return '\n'.join([getattr(schedule, 'dates_recurrence', None)
                          for schedule in self.schedules])

    @property
    def artists_ids(self):
        return [str(get_oid(a)) for a in self.artists]

    @property
    def relevant_data(self):
        result = super(CulturalEvent, self).relevant_data
        result.extend([', '.join([a.title for a in self.artists]),
                       ', '.join([to_localized_time(
                                  d, format_id='direct_literal',
                                  add_day_name=True, translate=True)
                                  for d in occurences_start(self, 'dates')]),
                       ', '.join([s.venue.city for s in self.schedules
                                  if s.venue]),
                       ', '.join([s.venue.title for s in self.schedules
                                  if s.venue])])
        return result

    @property
    def improved_cultural_event(self):
        original = getattr(self, 'original', None)
        return original if original is not self else None

    @property
    def substitutions(self):
        return [s for s in self.schedules if 'archived' not in s.state]

    @property
    def venues(self):
        return [s.venue for s in self.schedules if s.venue]

    def get_ticketing_url(self):
        ticketing_url = getattr(self, 'ticketing_url', None)
        if ticketing_url:
            return ticketing_url

        schedules = [s for s in self.schedules
                     if 'archived' not in s.state and
                        getattr(s, 'ticketing_url', None) and
                        s.ticket_type != 'Free admission']
        if schedules:
            return schedules[0].ticketing_url

        return None

    def get_contacts(self):
        if getattr(self, 'contacts', []):
            return getattr(self, 'contacts')
        else:
            return [venue.contacts[0] for venue
                    in set(self.venues) if venue.contacts]

    def get_zipcodes(self):
        zipcodes = [s.venue.zipcodes for s in self.schedules
                    if s.venue]
        return [item for sublist in zipcodes for item in sublist]

    def get_more_contents_criteria(self):
        "return specific query, filter values"
        query, args = super(CulturalEvent, self).get_more_contents_criteria()
        zipcodes = self.get_zipcodes()
        if zipcodes:
            args['geographic_filter'] = {'valid_zipcodes': zipcodes,
                                         'zipcode': zipcodes}

        return query, args

    def get_visibility_filter(self):
        result = super(CulturalEvent, self).get_visibility_filter()
        zipcodes = self.get_zipcodes()
        authors = [self.author] if self.author else []
        result.update({
            'contribution_filter': {'authors': authors},
            'geographic_filter': {'valid_zipcodes': zipcodes,
                                  'zipcode': zipcodes}})
        return result

    def get_valid_schedules(self):
        return [s for s in self.schedules if 'archived' not in s.state]

    def get_duplicates(self, states=('published', )):
        return find_duplicates_cultural_events(self, states)
