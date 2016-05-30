# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select

from lac.content.processes.services_processes.behaviors import (
    EditImportService)
from lac.content.service import (
    ImportServiceSchema, ImportService)
from lac import _


@view_config(
    name='editimportservice',
    context=ImportService,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditImportServiceView(FormView):

    title = _('Edit a import service')
    schema = select(ImportServiceSchema(factory=ImportService,
                                        editable=True),
               ['title', 'sources'])
    behaviors = [EditImportService, Cancel]
    formid = 'formeditimportservice'
    name = 'editimportservice'

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update({EditImportService: EditImportServiceView})
