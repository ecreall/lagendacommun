# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config


from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.view import BasicView
from pontus.view_operation import MultipleView

from lac.content.processes.admin_process.behaviors import (
    RemoveSmartFolder)
from lac.content.smart_folder import SmartFolder
from lac import _



class RemoveSmartFolderViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/admin_process/templates/alert_smartfolder_remove.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates:[item]}
        return result


class RemoveSmartFolderView(FormView):
    title = _('Remove')
    name = 'removesmartfolderform'
    formid = 'formremovesmartfolder'
    behaviors = [RemoveSmartFolder, Cancel]
    validate_behaviors = False


@view_config(
    name='removesmartfolder',
    context=SmartFolder,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemoveSmartFolderViewMultipleView(MultipleView):
    title = _('Remove the smart folder')
    name = 'removesmartfolder'
    viewid = 'removesmartfolder'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemoveSmartFolderViewStudyReport, RemoveSmartFolderView)
    validators = [RemoveSmartFolder.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RemoveSmartFolder: RemoveSmartFolderViewMultipleView})
