# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import (
    DEFAULTMAPPING_ACTIONS_VIEWS)

from pontus.view import BasicView

from lac.content.processes.lac_view_manager.behaviors import (
    SeeContributors)
from lac import _
from lac.core import ParticipativeEntity


@view_config(
    name='seecontributors',
    context=ParticipativeEntity,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeContributorsView(BasicView):
    title = _('Contributors')
    name = 'seecontributors'
    behaviors = [SeeContributors]
    template = 'lac:views/lac_view_manager/templates/contributors.pt'
    viewid = 'seecontributors'

    def update(self):
        self.execute(None)
        result = {}
        values = {'contributors': self.context.contributors}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update({SeeContributors: SeeContributorsView})
