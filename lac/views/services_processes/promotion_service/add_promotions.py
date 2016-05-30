# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi
import colander
from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import Schema, omit, select
from pontus.widget import (
    SequenceWidget, SimpleMappingWidget)

from lac.content.processes.services_processes.promotion_service.behaviors import (
    AddPromotions)
from lac.core import (
    SearchableEntity)
from lac import _


class PromotionSchema(Schema):

    title = colander.SchemaNode(
        colander.String(),
        title=_('Title'),
        )

    url = colander.SchemaNode(
        colander.String(),
        title=_('URL'),
        )


class PromotionsSchema(Schema):

    promotions = colander.SchemaNode(
        colander.Sequence(),
        omit(select(PromotionSchema(name='promotion',
                                  widget=SimpleMappingWidget(
                                  css_class='contact-well object-well default-well')),
                    ['title', 'url']),
            ['_csrf_token_']),
        widget=SequenceWidget(
            min_len=1,
            add_subitem_text_template=_('Add a new promotion')),
        title=_('Promotions')
        )


@view_config(
    name='addpromotions',
    context=SearchableEntity,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class AddPromotionsView(FormView):

    title = _('Add promotions')
    schema = select(PromotionsSchema(editable=True),
                    ['promotions'])
    behaviors = [AddPromotions, Cancel]
    formid = 'formaddpromotions'
    name = 'addpromotions'

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {AddPromotions: AddPromotionsView})
