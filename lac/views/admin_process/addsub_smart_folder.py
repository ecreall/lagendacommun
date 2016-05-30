# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select

from lac.content.processes.admin_process.behaviors import (
    AddSubSmartFolder)
from lac.content.smart_folder import (
    SmartFolderSchema, SmartFolder)
from lac import _


@view_config(
    name='addsubsmartfolder',
    context=SmartFolder,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class AddSubSmartFolderView(FormView):

    title = _('Add smart folder')
    schema = select(SmartFolderSchema(factory=SmartFolder, editable=True),
                    ['title',
                     'description',
                     'filters',
                     'view_type',
                     'classifications',
                     'style'])
    behaviors = [AddSubSmartFolder, Cancel]
    formid = 'formaaddsubsmartfolder'
    name = 'addsubsmartfolder'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/smart_folder_management.js']}


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {AddSubSmartFolder: AddSubSmartFolderView})
