# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from substanced.util import Batch

from dace.util import getSite
from dace.objectofcollaboration.principal.util import has_role
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from dace.objectofcollaboration.principal.util import get_current
from pontus.view import BasicView

from lac.content.processes.user_management.behaviors import (
    SeePerson)
from lac.content.person import Person
from lac.views.lac_view_manager.search import (
    SearchResultView)
from lac.core import BATCH_DEFAULT_SIZE, can_access
from lac.content.processes import get_states_mapping
from lac.utilities.utils import (
    generate_navbars,
    ObjectRemovedException)


@view_config(
    name='seeperson',
    context=Person,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeePersonView(BasicView):
    title = ''
    name = 'seeperson'
    behaviors = [SeePerson]
    template = 'lac:views/user_management/templates/see_person.pt'
    viewid = 'seeperson'

    def update(self):
        self.execute(None)
        try:
            navbars = generate_navbars(self, self.context, self.request)
        except ObjectRemovedException:
            return HTTPFound(self.request.resource_url(getSite(), ''))

        user = self.context
        current_user = get_current()
        objects = []
        is_current_user = current_user is user
        if is_current_user:
            objects = [o for o in getattr(user, 'all_contributions', [])
                       if 'archived' not in o.state]

        else:
            objects = [o for o in getattr(user, 'all_contributions', [])
                       if 'archived' not in o.state and
                       can_access(current_user, o)]

        objects = sorted(
            objects,
            key=lambda e: getattr(e, 'release_date', e.modified_at),
            reverse=True)
        batch = Batch(objects, self.request, default_size=BATCH_DEFAULT_SIZE)
        batch.target = "#results_contents"
        len_result = batch.seqlen
        result_body = []
        result = {}
        for obj in batch:
            object_values = {'object': obj,
                             'current_user': current_user,
                             'state': is_current_user and \
                                      get_states_mapping(current_user, obj,
                                            getattr(obj, 'state_or_none', [None])[0]) or \
                                      None
                             }
            body = self.content(args=object_values,
                                template=obj.templates['default'])['body']
            result_body.append(body)

        values = {'bodies': result_body,
                  'length': len_result,
                  'batch': batch
                  }
        contents_body = self.content(args=values,
                                     template=SearchResultView.template)['body']
        values = {'contents': (result_body and contents_body) or None,
                  'proposals': None,
                  'user': self.context,
                  'state': get_states_mapping(current_user, user,
                                getattr(user, 'state_or_none', [None])[0]),
                  'navbar_body': navbars['navbar_body'],
                  'footer_body': navbars['footer_body'],
                  'admin': has_role(role=('Admin',)),
                  'is_portal_manager': has_role(role=('PortalManager',)),
                  'len_contents': len_result}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        item['messages'] = navbars['messages']
        item['isactive'] = navbars['isactive']
        result.update(navbars['resources'])
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update(
  {SeePerson: SeePersonView})
