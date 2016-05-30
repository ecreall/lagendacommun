# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from zope.interface import implementer

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer, get_oid

from dace.util import get_obj, getSite
from dace.descriptors import SharedUniqueProperty
from pontus.widget import AjaxSelect2Widget
from pontus.file import Object as ObjectType

from .interface import IInterview
from lac import _, log
from lac.core import BaseReview
from lac.core_schema import BaseReviewSchema


def context_is_a_interview(context, request):
    return request.registry.content.istype(context, 'interview')


@colander.deferred
def review_choice(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    root = getSite()
    values = []
    if context is not root:
        review = context.review
        if review:
            values = [(get_oid(review), review.title)]

    ajax_url = request.resource_url(context,
                                    '@@creationculturelapi',
                                    query={'op': 'find_base_review'})

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
        css_class="artists-container review-artists",
        multiple=False,
        title_getter=title_getter,
        ajax_item_template='formatReview'
        )


class InterviewSchema(BaseReviewSchema):
    """Schema for interview"""

    name = NameSchemaNode(
        editing=context_is_a_interview,
        )

    review = colander.SchemaNode(
        ObjectType(),
        widget=review_choice,
        missing=None,
        title=_("Review")
        )


@content(
    'interview',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IInterview)
class Interview(BaseReview):
    """Interview class"""

    type_title = _('Interview')
    icon = 'lac-icon icon-interview'
    templates = {'default': 'lac:views/templates/interview_result.pt',
                 'bloc': 'lac:views/templates/interview_result_bloc.pt'}
    name = renamer()
    review = SharedUniqueProperty('review')
