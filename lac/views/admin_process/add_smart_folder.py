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
    AddSmartFolder)
from lac.content.smart_folder import (
    SmartFolderSchema, SmartFolder)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _


@view_config(
    name='addsmartfolder',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class AddSmartFolderView(FormView):

    title = _('Add smart folder')
    schema = select(SmartFolderSchema(factory=SmartFolder, editable=True),
                    ['title',
                     'description',
                     'filters',
                     'view_type',
                     'classifications',
                     'icon_data',
                     'style',
                     'add_as_a_block'])
    behaviors = [AddSmartFolder, Cancel]
    formid = 'formaddsmartfolder'
    name = 'addsmartfolder'
    requirements = {'css_links':[],
                    'js_links':['lac:static/js/smart_folder_management.js',
                                'lac:static/js/contextual_help_smart_folder.js']}


DEFAULTMAPPING_ACTIONS_VIEWS.update({AddSmartFolder: AddSmartFolderView})