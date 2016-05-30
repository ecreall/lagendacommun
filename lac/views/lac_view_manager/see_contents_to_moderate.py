# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from substanced.util import Batch

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from dace.objectofcollaboration.principal.util import get_current
from pontus.view import BasicView

from lac.content.processes.lac_view_manager.behaviors import (
    SeeContentsToModerate)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _
from lac.content.processes import get_states_mapping
from lac import core
from lac.views.filter import (
    get_filter, merge_with_filter_view, FILTER_SOURCES, find_entities)


CONTENTS_MESSAGES = {
        '0': _(u"""No element found"""),
        '1': _(u"""One element found"""),
        '*': _(u"""${nember} elements found""")
        }


@view_config(
    name='contentstomoderate',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeContentsToModerateView(BasicView):
    title = _('Contents to moderate')
    name = 'contentstomoderate'
    behaviors = [SeeContentsToModerate]
    template = 'lac:views/lac_view_manager/templates/search_result.pt'
    viewid = 'contentstomoderate'

    def _add_filter(self, user):
        def source(**args):
            content_types = list(core.SEARCHABLE_CONTENTS.keys())
            metadata_filter = args.get('metadata_filter', {})
            if 'content_types' not in metadata_filter:
                metadata_filter['content_types'] = content_types
                args['metadata_filter'] = metadata_filter

            objects = find_entities(user=user, sort_on=None,
                include_site=True, **args)
            return objects

        url = self.request.resource_url(self.context, '@@creationculturelapi')
        return get_filter(
            self,
            url=url,
            source=source,
            select=['metadata_filter', 'geographic_filter',
                    'contribution_filter', 'temporal_filter',
                    'text_filter', 'other_filter'])

    def update(self):
        self.execute(None)
        user = get_current()
        filter_form, filter_data = self._add_filter(user)
        content_types = list(core.SEARCHABLE_CONTENTS.keys())
        args = {'metadata_filter': {'content_types': content_types}}
        args = merge_with_filter_view(self, args)
        args['request'] = self.request
        objects = find_entities(user=user,
                                sort_on='release_date', reverse=True,
                                include_site=True,
                                **args)
        url = self.request.resource_url(self.context, 'contentstomoderate')
        batch = Batch(objects, self.request,
                      url=url,
                      default_size=core.BATCH_DEFAULT_SIZE)
        batch.target = "#results_contents"
        len_result = batch.seqlen
        index = str(len_result)
        if len_result > 1:
            index = '*'

        self.title = _(CONTENTS_MESSAGES[index],
                       mapping={'nember': len_result})
        filter_data['filter_message'] = self.title
        filter_body = self.filter_instance.get_body(filter_data)
        result_body = []
        for obj in batch:
            render_dict = {'object': obj,
                           'current_user': user,
                           'state': get_states_mapping(user, obj,
                                   getattr(obj, 'state_or_none', [None])[0])}
            body = self.content(args=render_dict,
                                template=obj.templates['default'])['body']
            result_body.append(body)

        result = {}
        values = {'bodies': result_body,
                  'batch': batch,
                  'filter_body': filter_body}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        result['css_links'] = filter_form['css_links']
        result['js_links'] = filter_form['js_links']
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {SeeContentsToModerate: SeeContentsToModerateView})


FILTER_SOURCES.update(
    {SeeContentsToModerateView.name: SeeContentsToModerateView})
