# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from pyramid.view import view_config

from substanced.util import get_oid

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from dace.objectofcollaboration.entity import Entity
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select, Schema
from pontus.widget import Select2Widget

from lac.content.processes.admin_process.behaviors import (
    FixAccessPerimeter)
from lac import _


@colander.deferred
def sources_choices(node, kw):
    request = node.bindings['request']
    values = []
    values = [(str(get_oid(s)), s.title) for s in
              getattr(request.root, 'site_folders', [])]
    values = sorted(values, key=lambda e: e[1])
    values.insert(0, ('self', _('This site')))
    values.insert(0, ('all', _('All sites')))
    return Select2Widget(values=values, multiple=True)


class AccessPerimeterSchema(Schema):

    access_control = colander.SchemaNode(
        colander.Set(),
        widget=sources_choices,
        title=_('Access perimeter'),
        default=['all']
        )


@view_config(
    name='fixaccessperimeter',
    context=Entity,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class FixAccessPerimeterView(FormView):

    title = _('Setup the access perimeter')
    schema = select(AccessPerimeterSchema(),
                    ['access_control'])
    behaviors = [FixAccessPerimeter, Cancel]
    formid = 'formfixaccessperimeter'
    name = 'fixaccessperimeter'

    def default_data(self):
        access_control = getattr(self.context,
                                 'access_control', ['all'])
        return {'access_control': [str(obj) for obj in access_control]}


DEFAULTMAPPING_ACTIONS_VIEWS.update({FixAccessPerimeter: FixAccessPerimeterView})
