# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select

from lac.content.processes.lac_file_management.behaviors import (
    EditFile)
from lac.core import FileSchema, FileEntity
from lac import _


@view_config(
    name='editfile',
    context=FileEntity,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditFileView(FormView):

    title = _('Edit the file')
    schema = select(FileSchema(factory=FileEntity, editable=True),
                    ['title',
                     'description',
                     'text'])
    behaviors = [EditFile, Cancel]
    formid = 'formeditfile'
    name = 'editfile'

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update({EditFile: EditFileView})