# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from zope.interface import implementer

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer


from .interface import IReview
from lac import _
from lac.core import BaseReview
from lac.core_schema import BaseReviewSchema


def context_is_a_review(context, request):
    return request.registry.content.istype(context, 'review')


class ReviewSchema(BaseReviewSchema):
    """Schema for review"""

    name = NameSchemaNode(
        editing=context_is_a_review,
        )


@content(
    'review',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IReview)
class Review(BaseReview):
    """Review class"""

    type_title = _('Review')
    icon = 'glyphicon glyphicon-file'
    templates = {'default': 'lac:views/templates/review_result.pt',
                 'bloc': 'lac:views/templates/review_result_bloc.pt'}
    name = renamer()
