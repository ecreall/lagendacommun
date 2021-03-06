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
    WithdrawSmartFolder)
from lac.content.smart_folder import SmartFolder
from lac import _



class WithdrawSmartFolderViewStudyReport(BasicView):
    title = 'Alert for withdraw'
    name = 'alertforwithdraw'
    template = 'lac:views/admin_process/templates/alert_smartfolder_withdraw.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class WithdrawSmartFolderView(FormView):
    title = _('Withdraw')
    name = 'withdrawsmartfolderform'
    formid = 'formwithdrawsmartfolder'
    behaviors = [WithdrawSmartFolder, Cancel]
    validate_behaviors = False


@view_config(
    name='withdrawsmartfolder',
    context=SmartFolder,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class WithdrawSmartFolderViewMultipleView(MultipleView):
    title = _('Withdraw the smart folder')
    name = 'withdrawsmartfolder'
    viewid = 'withdrawsmartfolder'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (WithdrawSmartFolderViewStudyReport, WithdrawSmartFolderView)
    validators = [WithdrawSmartFolder.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {WithdrawSmartFolder: WithdrawSmartFolderViewMultipleView})
