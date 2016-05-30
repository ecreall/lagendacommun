# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from persistent.dict import PersistentDict
from zope.interface import implementer


from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer, get_oid

from dace.descriptors import (
    SharedUniqueProperty,
    CompositeUniqueProperty)
from dace.util import get_obj, getSite
from pontus.widget import (
    Select2Widget,
    RichTextWidget,
    AjaxSelect2Widget)
from pontus.file import ObjectData, Object as ObjectType
from pontus.core import (
    VisualisableElementSchema, VisualisableElement)

from .interface import IGame
from lac import _, log
from lac.core import (
    ADVERTISING_CONTAINERS,
    SearchableEntitySchema,
    SearchableEntity)
from lac.core_schema import picture_widget
from lac.file import Image
from lac.utilities.utils import html_to_text


def context_is_a_game(context, request):
    return request.registry.content.istype(context, 'game')


@colander.deferred
def winners_widget(node, kw):
    context = node.bindings['context']
    participants = getattr(context, 'participants', {})
    values = [(u, participants[u]['title']) for u in participants]
    values = sorted(values,
                    key=lambda e: e[1])
    return Select2Widget(
        values=values,
        multiple=True)


@colander.deferred
def participants_widget(node, kw):
    context = node.bindings['context']
    participants = getattr(context, 'participants', {})
    values = [(u, participants[u]['title']) for u in participants]
    values = sorted(values,
                    key=lambda e: e[1])
    return Select2Widget(
        values=values,
        multiple=True)


@colander.deferred
def announcement_choice(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    root = getSite()
    values = []
    if context is not root:
        announcement = context.announcement
        if announcement:
            values = [(get_oid(announcement), announcement.title)]

    ajax_url = request.resource_url(context,
                                    '@@creationculturelapi',
                                    query={'op': 'find_cultural_events'})
    def title_getter(id):
        try:
            obj = get_obj(int(id), None)
            if obj:
                return obj.title
            else:
                return id
        except Exception as e:
            log.warning(e)
            return id

    return AjaxSelect2Widget(
        values=values,
        ajax_url=ajax_url,
        multiple=False,
        title_getter=title_getter
        )


@colander.deferred
def position_widget(node, kw):
    values = [(ad_id, value['title'])
              for ad_id, value in ADVERTISING_CONTAINERS.items()
              if 'game' in value['tags']]
    values = sorted(values,
                    key=lambda e: ADVERTISING_CONTAINERS[e[0]]['order'])
    return Select2Widget(
        css_class="advertising-positions",
        values=values,
        multiple=True)


class GameSchema(VisualisableElementSchema, SearchableEntitySchema):
    """Schema for Web advertising"""

    name = NameSchemaNode(
        editing=context_is_a_game,
        )

    description = colander.SchemaNode(
        colander.String(),
        widget=RichTextWidget(),
        title=_("Description"),
        missing=""
        )

    winners = colander.SchemaNode(
        colander.Set(),
        widget=winners_widget,
        title=_('Winners')
        )

    winner_number = colander.SchemaNode(
        colander.Int(),
        title=_('Winner number')
        )

    participants = colander.SchemaNode(
        colander.Set(),
        widget=participants_widget,
        title=_('Participants')
        )

    start_date = colander.SchemaNode(
        colander.DateTime(),
        title=_('Start date')
        )

    end_date = colander.SchemaNode(
        colander.DateTime(),
        title=_('End date')
        )

    announcement = colander.SchemaNode(
        ObjectType(),
        widget=announcement_choice,
        missing=None,
        title=_("Cultural event")
        )

    picture = colander.SchemaNode(
        ObjectData(Image),
        widget=picture_widget,
        title=_('Picture'),
        missing=None
        )


@content(
    'game',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IGame)
class Game(VisualisableElement, SearchableEntity):
    """Game class"""

    type_title = _('Game')
    icon = 'glyphicon glyphicon-bishop'
    templates = {'default': 'lac:views/templates/game_result.pt',
                 'bloc': 'lac:views/templates/game_result.pt'}
    name = renamer()
    picture = CompositeUniqueProperty('picture')
    author = SharedUniqueProperty('author', 'contents')
    announcement = SharedUniqueProperty('announcement')

    def __init__(self, **kwargs):
        self.click = 0
        super(Game, self).__init__(**kwargs)
        self.access_control = [self.source_site]
        self.participants = PersistentDict()
        self.winners = PersistentDict()

    def _init_presentation_text(self):
        self._presentation_text = html_to_text(
            getattr(self, 'description', ''))

    def presentation_text(self, nb_characters=400):
        text = getattr(self, '_presentation_text', None)
        if text is None:
            self._init_presentation_text()
            text = getattr(self, '_presentation_text', '')

        return text[:nb_characters]+'...'

    def get_participants_by_mail(self, mails):
        result = {}
        for mail in [m for m in mails if m in self.participants]:
            result[mail] = self.participants[mail]

        return result
