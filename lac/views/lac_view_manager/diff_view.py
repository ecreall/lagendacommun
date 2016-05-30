# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.util import get_obj
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView, ViewError

from lac.content.processes.lac_view_manager.behaviors import (
    DiffView)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _, log


@view_config(
    name='diffview',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class DiffViewView(BasicView):

    title = _('Differences')
    behaviors = [DiffView]
    name = 'diffview'
    template = 'lac:views/lac_view_manager/templates/diff_template.pt'

    def update(self):
        source_oid = self.params('source')
        targets_oid = self.params('targets')
        if targets_oid and source_oid:
            try:
                if not isinstance(targets_oid, (list, tuple)):
                    targets_oid = [targets_oid]

                targets = [get_obj(int(t)) for t in targets_oid]
                source = get_obj(int(source_oid))
                if targets and source:
                    result = self.execute(
                        {'source': source,
                         'targets': targets})
                    if result:
                        values = result[0]
                        values['context'] = source
                        body = self.content(
                            args=values, template=self.template)['body']
                        item = self.adapt_item(body, self.viewid)
                        result = {}
                        result['coordinates'] = {self.coordinates: [item]}
                        return result

            except Exception as error:
                log.warning(error)

        view_error = ViewError()
        view_error.principalmessage = _("An error has occurred.")
        return self.failure(view_error)


DEFAULTMAPPING_ACTIONS_VIEWS.update({DiffView: DiffViewView})
