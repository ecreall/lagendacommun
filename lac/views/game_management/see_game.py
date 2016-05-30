# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from dace.util import getSite
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from dace.objectofcollaboration.principal.util import get_current, has_any_roles
from pontus.view import BasicView

from lac.content.processes.game_management.behaviors import (
    SeeGame)
from lac.content.game import Game
from lac.content.processes import get_states_mapping
from lac.utilities.utils import (
    generate_navbars,
    ObjectRemovedException,
    get_site_folder)


@view_config(
    name='seegame',
    context=Game,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeGameView(BasicView):
    title = ''
    name = 'seegame'
    viewid = 'seegame'
    behaviors = [SeeGame]
    template = 'lac:views/game_management/templates/see_game.pt'

    def update(self):
        self.execute(None)
        try:
            navbars = generate_navbars(self, self.context, self.request)
        except ObjectRemovedException:
            return HTTPFound(self.request.resource_url(getSite(), ''))

        result = {}
        user = get_current()
        site = get_site_folder(True)
        add_participants_view = False
        if not any(s in ('editable', 'rejected',
                         'submitted', 'prepublished')
                   for s in self.context.state):
            add_participants_view = has_any_roles(
                roles=(('GameResponsible', site), 'Admin'))

        values = {
            'object': self.context,
            'state': get_states_mapping(
                    user, self.context,
                    getattr(self.context, 'state_or_none', [None])[0]),
            'navbar_body': navbars['navbar_body'],
            'add_participants_view': add_participants_view
        }
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        item['messages'] = navbars['messages']
        item['isactive'] = navbars['isactive']
        result.update(navbars['resources'])
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update({SeeGame: SeeGameView})
