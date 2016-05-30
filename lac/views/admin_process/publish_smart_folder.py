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
    PublishSmartFolder)
from lac.content.smart_folder import SmartFolder
from lac import _



class PublishSmartFolderViewStudyReport(BasicView):
    title = 'Alert for publishing'
    name = 'alertforpublishing'
    template = 'lac:views/admin_process/templates/alert_smartfolder_publish.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class PublishSmartFolderView(FormView):
    title = _('Publish')
    name = 'publishsmartfolderform'
    formid = 'formpublishsmartfolder'
    behaviors = [PublishSmartFolder, Cancel]
    validate_behaviors = False


@view_config(
    name='publishsmartfolder',
    context=SmartFolder,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class PublishSmartFolderViewMultipleView(MultipleView):
    title = _('Publish the smart folder')
    name = 'publishsmartfolder'
    viewid = 'publishsmartfolder'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (PublishSmartFolderViewStudyReport, PublishSmartFolderView)
    validators = [PublishSmartFolder.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {PublishSmartFolder: PublishSmartFolderViewMultipleView})
