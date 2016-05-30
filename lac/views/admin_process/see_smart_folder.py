# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import math
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from substanced.util import Batch, get_oid

from dace.util import get_obj, getSite
from dace.objectofcollaboration.principal.util import get_current
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.view import BasicView, ViewError
from pontus.util import merge_dicts

from lac.content.processes.admin_process.behaviors import (
    SeeSmartFolder)
from lac.content.smart_folder import SmartFolder
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _, log
from lac.core import BATCH_DEFAULT_SIZE, can_access
from lac.content.processes import get_states_mapping
from lac.utilities.smart_folder_utility import (
    get_folder_content, get_adapted_filter)
from lac import CLASSIFICATIONS
from lac.utilities.utils import (
    generate_navbars,
    ObjectRemovedException,
    get_site_folder)
from lac.views.filter import (
    get_filter, FILTER_SOURCES, merge_with_filter_view, repr_filter)


@view_config(
    name='seesmartfolder',
    context=SmartFolder,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeSmartFolderView(BasicView):
    title = ''
    name = 'seesmartfolder'
    behaviors = [SeeSmartFolder]
    template = 'lac:views/admin_process/templates/see_smartfolder.pt'
    subfoldertemplate = 'lac:views/admin_process/templates/see_smartfolders.pt'
    viewid = 'seesmartfolder'
    requirements = {'css_links': ['deform_treepy:static/vakata-jstree/dist/themes/default/style.min.css'],
                    'js_links': ['deform_treepy:static/js/treepy.js',
                                 'deform_treepy:static/vakata-jstree/dist/jstree.js']}

    def update(self):
        self.execute(None)
        try:
            navbars = generate_navbars(self, self.context, self.request)
        except ObjectRemovedException:
            return HTTPFound(self.request.resource_url(getSite(), ''))

        site = get_site_folder(True)
        site_id = get_oid(site)
        user = get_current()
        result = {}
        subfolders = [sf for sf in self.context.children
                      if can_access(user, sf)]
        subfolders = sorted(subfolders, key=lambda e: e.get_order(site_id))
        values = {'folders': subfolders,
                  'row_len': math.ceil(len(subfolders)/6),
                  'actions_bodies': []}
        subbody = self.content(args=values,
                               template=self.subfoldertemplate)['body']
        def get_title(control):
            try:
                obj = get_obj(int(control))
            except:
                return control

            return obj.title if obj else control

        access_control = [get_title(s) for s in
                          getattr(self.context, 'access_control', [_('All sites')])]
        values = {'object': self.context,
                  'subfolders': subfolders,
                  'filter': repr_filter(getattr(self.context, 'filters', []),
                                        self.request),
                  'subfolders_body': subbody,
                  'navbar_body': navbars['navbar_body'],
                  'actions_bodies': navbars['body_actions'],
                  'access_control': access_control
                  }
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        item['messages'] = navbars['messages']
        item['isactive'] = navbars['isactive']
        result.update(navbars['resources'])
        result.update(self.requirements)
        result['coordinates'] = {self.coordinates: [item]}
        return result


@view_config(
    name='open',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class OpenFolderView(BasicView):
    title = _('Open a folder')
    name = 'open'
    breadcrumb_template = 'lac:views/templates/folder_breadcrumb.pt'
    templates = {'default': 'lac:views/lac_view_manager/templates/search_result.pt',
                 'bloc': 'lac:views/lac_view_manager/templates/search_result_blocs.pt'}
    viewid = 'open_folder'
    wrapper_template = 'lac:views/admin_process/templates/folder_view_wrapper.pt'
    css_class = "open-folder"

    def _add_filter(self, folder, user):
        def source(**args):
            objects = get_folder_content(folder, user, sort_on=None, **args)
            return objects

        url = self.request.resource_url(
            self.context,
            '@@creationculturelapi',
            query={'folderid': self.params('folderid')})
        fields = get_adapted_filter(folder, user)
        if not fields:
            return None, None

        return get_filter(
            self, url=url,
            source=source,
            **fields)

    def update(self):
        result = {}
        user = get_current()
        folderid = self.params('folderid')
        try:
            folder = get_obj(int(folderid))
        except:
            folder = None
        # if not valid folderid
        if folderid is None or folder is None:
            error = ViewError()
            error.principalmessage = _("Access to the requested folder has been denied")
            error.causes = [_("Folder not valid")]
            message = error.render_message(self.request)
            item = self.adapt_item('', self.viewid)
            item['messages'] = {error.type: [message]}
            result['coordinates'] = {self.coordinates: [item]}
            return result

        # if permission denied
        if folder and not can_access(user, folder):
            error = ViewError()
            error.principalmessage = _("Access to the requested folder has been denied")
            error.causes = [_("Permission denied")]
            message = error.render_message(self.request)
            item = self.adapt_item('', self.viewid)
            item['messages'] = {error.type: [message]}
            result['coordinates'] = {self.coordinates: [item]}
            return result

        classifications = [CLASSIFICATIONS[fid] for fid
                           in getattr(folder, 'classifications', [])]
        classifications.reverse()
        source_class = None
        for classification in classifications:
            source_class = classification(source_class)

        setattr(self, 'filter_instance', None)
        filter_body = None
        filter_form, filter_data = self._add_filter(folder, user)
        # calling self._add_filter will set self.filter_instance or not
        template_type = getattr(folder, 'view_type', 'default')
        if template_type == 'bloc':
            self.container_css_class = 'home folder-bloc'
            self.wrapper_template = 'lac:views/admin_process/templates/folder_blocs_view_wrapper.pt'

        args = merge_with_filter_view(self, {})
        objects = get_folder_content(folder, user, **args)
        len_result = len(objects)
        self.breadcrumb = self.content(
            args={'lineage': folder.folder_lineage,
                  'nember': len_result},
            template=self.breadcrumb_template)['body']
        self.title = '/'.join([f.title for f in folder.folder_lineage])
        if getattr(self, 'filter_instance', None) is not None:
            filter_data['filter_message'] = self.breadcrumb
            filter_body = getattr(self, 'filter_instance').get_body(filter_data)

        if source_class is None:
            url = self.request.resource_url(
                self.context, 'open', query={'folderid': folderid})
            batch = Batch(objects,
                          self.request,
                          url=url,
                          default_size=BATCH_DEFAULT_SIZE)
            batch.target = "#results"
            result_body = []
            for obj in batch:
                object_values = {'object': obj,
                                 'current_user': user,
                                 'state': get_states_mapping(
                                     user, obj,
                                     getattr(obj, 'state_or_none', [None])[0])}
                body = self.content(
                    args=object_values,
                    template=obj.templates[template_type])['body']
                result_body.append(body)

            values = {
                'bodies': result_body,
                'batch': batch,
                'filter_body': filter_body,
                'row_len': math.ceil(len_result/2)
                }
            template = self.templates.get(template_type, 'default')
            body = self.content(args=values, template=template)['body']
        else:

            body = source_class.render(
                objects, self.request,
                folder, filter_body=filter_body,
                validated=getattr(self.filter_instance, 'validated', {}),
                template_type=template_type)

        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        result = merge_dicts(self.requirements_copy, result)
        if filter_form:
            result['css_links'] = filter_form['css_links']
            result['js_links'] = filter_form['js_links']

        return result

    def before_update(self):
        super(OpenFolderView, self).before_update()
        folderid = self.params('folderid')
        try:
            folder = get_obj(int(folderid))
            if folder:
                self.title = '/'.join([f.title for f in folder.folder_lineage])
        except (TypeError, ValueError):
            self.title = self.request.localizer.translate(_('Folder not valid'))
            user = get_current()
            log.info(
                "Folder not valid. id: ({folderid}) , user: ({user}, {email}) ".format(
                    user=getattr(user, 'title', getattr(user, 'name', 'Anonymous')),
                    email=getattr(user, 'email', 'Anonymous'),
                    folderid=folderid))


DEFAULTMAPPING_ACTIONS_VIEWS.update({SeeSmartFolder: SeeSmartFolderView})

FILTER_SOURCES.update({OpenFolderView.name: OpenFolderView})
