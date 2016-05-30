# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from substanced.util import Batch

from dace.objectofcollaboration.principal.util import get_current
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView

from lac.views.filter import find_entities
from lac.content.interface import IOrganization
from lac.content.processes.organization_management.behaviors import (
    SeeOrganizations)
from lac.content.lac_application import CreationCulturelleApplication
from lac.core import BATCH_DEFAULT_SIZE
from lac import _


CONTENTS_MESSAGES = {
        '0': _(u"""No organization found"""),
        '1': _(u"""One organization found"""),
        '*': _(u"""${nember} organizations found""")
        }


@view_config(
    name='seeorganizations',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeOrganizationsView(BasicView):
    title = _('Organizations')
    name = 'seeorganizations'
    behaviors = [SeeOrganizations]
    template = 'lac:views/lac_view_manager/templates/search_result.pt'
    viewid = 'seeorganizations'

    def update(self):
        self.execute(None)
        objects = find_entities(
            user=get_current(),
            interfaces=[IOrganization],
            sort_on='modified_at', reverse=True)
        batch = Batch(objects, self.request, default_size=BATCH_DEFAULT_SIZE)
        batch.target = "#results_organizations"
        len_result = batch.seqlen
        index = str(len_result)
        if len_result > 1:
            index = '*'

        self.title = _(CONTENTS_MESSAGES[index],
                       mapping={'nember': len_result})
        result_body = []
        for obj in batch:
            object_values = {'object': obj}
            body = self.content(args=object_values,
                                template=obj.templates['default'])['body']
            result_body.append(body)

        result = {}
        values = {
                'bodies': result_body,
                'length': len_result,
                'batch': batch,
               }
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result

DEFAULTMAPPING_ACTIONS_VIEWS.update({SeeOrganizations: SeeOrganizationsView})
