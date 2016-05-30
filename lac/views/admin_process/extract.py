# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select

from lac.content.processes.admin_process.behaviors import (
    Extract)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac.content.smart_folder import (
    SmartFolderSchema, classifications_widget, classifications_seq_widget)
from lac import _


class ExtractSchema(SmartFolderSchema):
    classifications = colander.SchemaNode(
        colander.Sequence(),
        colander.SchemaNode(
            colander.String(),
            widget=classifications_widget,
            name=_("Classification")
            ),
        widget=classifications_seq_widget,
        title=_('Classifications'),
        description=_('Select one or more options of classification.'),
        validator=colander.Length(min=1)
        )


@view_config(
    name='extract',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ExtractView(FormView):

    title = _('Extract')
    schema = select(ExtractSchema(),
                    ['filters',
                     'classifications',
                     ])
    behaviors = [Extract, Cancel]
    formid = 'formextract'
    name = 'extract'


DEFAULTMAPPING_ACTIONS_VIEWS.update({Extract: ExtractView})
