# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from zope.interface import implementer

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer

from dace.objectofcollaboration.entity import Entity
from dace.descriptors import SharedMultipleProperty, SharedUniqueProperty
from pontus.core import VisualisableElement, VisualisableElementSchema

from .interface import IOrder
from lac import _


def context_is_a_order(context, request):
    return request.registry.content.istype(context, 'order')


class OrderSchema(VisualisableElementSchema):
    """Schema for order"""

    name = NameSchemaNode(
        editing=context_is_a_order,
        )

    title = colander.SchemaNode(
        colander.String(),
        title=_('Title')
        )


@content(
    'order',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IOrder)
class Order(VisualisableElement, Entity):
    """Order class"""

    name = renamer()
    icon = 'glyphicon glyphicon-barcode'
    templates = {'default': 'lac:views/templates/order_result.pt',
                 'bloc': 'lac:views/templates/order_result.pt'}
    products = SharedMultipleProperty('products',
                                      'order')
    customeraccount = SharedUniqueProperty('customeraccount',
                                           'orders')

    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)
        self.set_data(kwargs)

    @property
    def total(self):
        return sum([float(product.get_price()) for
                    product in self.products])
