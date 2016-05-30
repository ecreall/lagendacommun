# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from substanced.util import Batch, get_oid

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from dace.objectofcollaboration.principal.util import get_current

from pontus.view import BasicView

from lac.content.processes.lac_view_manager.behaviors import (
    SeeGames)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _
from lac.core import BATCH_DEFAULT_SIZE
from lac.views.filter import find_entities
from lac.content.interface import IGame
from lac.utilities.utils import get_site_folder


CONTENTS_MESSAGES = {
    '0': _(u"""No game found"""),
    '1': _(u"""One game found"""),
    '*': _(u"""${nember} games found""")
    }


@view_config(
    name='seegames',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeGamesView(BasicView):
    title = _('Games & Competitions')
    name = 'seegames'
    behaviors = [SeeGames]
    template = 'lac:views/lac_view_manager/templates/search_result.pt'
    viewid = 'seegames'

    def update(self):
        self.execute(None)
        user = get_current()
        site = str(get_oid(get_site_folder(True)))
        games = find_entities(
            interfaces=[IGame],
            metadata_filter={'states': ['published']},
            other_filter={'sources': [site]},
            force_publication_date=True)

        batch = Batch(games, self.request,
                      default_size=BATCH_DEFAULT_SIZE)
        batch.target = "#results_contents"
        len_result = batch.seqlen
        index = str(len_result)
        if len_result > 1:
            index = '*'

        self.title = _(CONTENTS_MESSAGES[index],
                       mapping={'nember': len_result})
        result_body = []
        for obj in batch:
            render_dict = {'object': obj,
                           'current_user': user,
                           'state': None}
            body = self.content(args=render_dict,
                                template=obj.templates['default'])['body']
            result_body.append(body)

        result = {}
        values = {'bodies': result_body,
                  'batch': batch}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update({SeeGames: SeeGamesView})
