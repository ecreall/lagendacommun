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
    RemoveSiteFolder)
from lac.content.site_folder import SiteFolder
from lac import _



class RemoveSiteFolderViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/admin_process/templates/alert_sitefolder_remove.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates:[item]}
        return result


class RemoveSiteFolderView(FormView):
    title =  _('Remove')
    name = 'removesitefolderform'
    formid = 'formremovesitefolder'
    behaviors = [RemoveSiteFolder, Cancel]
    validate_behaviors = False


@view_config(
    name='removesitefolder',
    context=SiteFolder,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class RemoveSiteFolderViewMultipleView(MultipleView):
    title = _('Remove the site folder')
    name = 'removesitefolder'
    viewid = 'removesitefolder'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (RemoveSiteFolderViewStudyReport, RemoveSiteFolderView)
    validators = [RemoveSiteFolder.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {RemoveSiteFolder: RemoveSiteFolderViewMultipleView})
