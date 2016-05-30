# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from zope.interface import implementer

from substanced.content import content
from substanced.schema import NameSchemaNode

from dace.util import getSite
from dace.descriptors import CompositeUniqueProperty

from pontus.file import ObjectData
from pontus.widget import ImageWidget

from pontus.form import FileUploadTempStore

from .interface import IFilmSchedule
from lac.core import SearchableEntitySchema, SearchableEntity
from lac import _
from .schedule import Schedule, ScheduleSchema
from lac.file import Image


def context_is_a_film_schedule(context, request):
    return request.registry.content.istype(context, 'film_schedule')


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
        source=source,
        selection_message=_("Upload image.")
        )


class FilmScheduleSchema(SearchableEntitySchema, ScheduleSchema):
    """Schema for film schedule"""

    name = NameSchemaNode(
        editing=context_is_a_film_schedule,
        )

    picture = colander.SchemaNode(
        ObjectData(Image),
        widget=picture_widget,
        description=_("Thank you to upload a picture and select an area of interest. "
                      "The different formats of the picture used on the site will be generated from this area."),
        title=_('Picture'),
        missing=None,
        )


@content(
    'film_schedule',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IFilmSchedule)
class FilmSchedule(SearchableEntity, Schedule):
    """Film schedule class"""

    type_title = _('Film schedule')
    icon = 'glyphicon glyphicon-film'
    templates = {'default': 'lac:views/templates/film_schedule_result.pt',
                 'bloc': 'lac:views/templates/film_schedule_result.pt',
                 'extraction': 'lac:views/templates/extraction/film_schedule_result.pt'}
    picture = CompositeUniqueProperty('picture')

    def __init__(self, **kwargs):
        super(FilmSchedule, self).__init__(**kwargs)
