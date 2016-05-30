# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from zope.interface import implementer
from collections import OrderedDict

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer, get_oid

from dace.descriptors import SharedMultipleProperty
from dace.util import getSite, get_obj
from pontus.schema import select, omit
from pontus.widget import (
    TextInputWidget,
    AjaxSelect2Widget,
    SimpleMappingWidget,
    SequenceWidget,
    RadioChoiceWidget
    )

from .interface import ICinemaReview
from lac import _, log
from lac.core import BaseReview
from lac.core_schema import BaseReviewSchema
from lac.content.artist import (
    ArtistInformationSheet, ArtistInformationSheetSchema)
from lac.views.widget import RichTextWidget


def render_appreciation(appreciation, text):
    return ("<div class=\"smileyface " +
            appreciation + "-smileyface\" title=\"" + text + "\">" +
            "<p class=\"eyes lefteye\"></p>" +
			"<p class=\"eyes righteye\"></p>" +
			"<div class=\""+appreciation+"\">" +
			"</div></div>")


APPRECIATIONS = OrderedDict(
	            [('excellent', _('Excellent')),
                 ('good', _('Good')),
                 ('passable', _('Passable')),
                 ('prettybad', _('Pretty bad')),
                 ('bad', _('Bad'))])


def context_is_a_cinema_review(context, request):
    return request.registry.content.istype(context, 'cinema_review')


@colander.deferred
def appreciation_choice(node, kw):
    request = node.bindings['request']
    localizer = request.localizer
    values = [(ap_id, render_appreciation(ap_id, localizer.translate(text)))
              for ap_id, text in APPRECIATIONS.items()]
    return RadioChoiceWidget(
        values=values,
        template='lac:views/'
                 'templates/radio_choice.pt',
        inline=True)


@colander.deferred
def directors_choice(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    root = getSite()
    values = []
    if context is not root:
        values = [(a.get_id(), a.title) for a in context.directors]

    ajax_url = request.resource_url(context,
                                    '@@creationculturelapi',
                                    query={'op': 'find_directors'})

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
        css_class="directors-container review-directors",
        multiple=True,
        create=True,
        title_getter=title_getter,
        ajax_item_template="artist_item_template",
        ajax_selection_template='formatDirector'
        )


class CinemaReviewSchema(BaseReviewSchema):
    """Schema for review"""

    name = NameSchemaNode(
        editing=context_is_a_cinema_review,
        )

    nationality = colander.SchemaNode(
        colander.String(),
        widget=TextInputWidget(),
        title=_("Nationality")
        )

    directors_ids = colander.SchemaNode(
        colander.Set(),
        widget=directors_choice,
        title=_('Directors'),
        missing=[]
        )

    directors = colander.SchemaNode(
        colander.Sequence(),
        omit(select(ArtistInformationSheetSchema(editable=True,
                                                 factory=ArtistInformationSheet,
                                                 omit=('id', ),
                            widget=SimpleMappingWidget(
                                  css_class='director-data object-well'
                                            ' default-well'),
                                  name=_('Director')),
                    ['id', 'origin_oid', 'title',
                    'description', 'picture', 'biography']),
            ['_csrf_token_', '__objectoid__']),
        widget=SequenceWidget(css_class='directors-values',
                            template='lac:views/'
                                     'templates/sequence_modal.pt',
                            item_template='lac:views/'
                                          'templates/sequence_modal_item.pt'),
        title=_('Directors'),
        )

    duration = colander.SchemaNode(
        colander.String(),
        widget=TextInputWidget(),
        title=_("Duration")
        )
    appreciation = colander.SchemaNode(
        colander.String(),
        widget=appreciation_choice,
        title=_("Appreciation")
        )
    opinion = colander.SchemaNode(
        colander.String(),
        widget=RichTextWidget(),
        title=_("Opinion")
        )


@content(
    'cinema_review',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(ICinemaReview)
class CinemaReview(BaseReview):
    """Review class"""

    type_title = _('Cinema review')
    icon = 'lac-icon icon-reviwe-cinema'
    templates = {'default': 'lac:views/templates/review_result.pt',
                 'bloc': 'lac:views/templates/review_result_bloc.pt'}
    name = renamer()
    directors = SharedMultipleProperty('directors', 'productions')

    @property
    def appreciation_title(self):
        return APPRECIATIONS.get(getattr(self, 'appreciation', ''), '')

    @property
    def directors_ids(self):
        return [str(get_oid(a)) for a in self.directors]

    @property
    def relevant_data(self):
        result = super(CinemaReview, self).relevant_data
        result.extend([', '.join([a.title for a in self.directors])])
        return result
