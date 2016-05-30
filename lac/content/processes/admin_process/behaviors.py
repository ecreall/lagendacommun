# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import pytz
from persistent.list import PersistentList
import datetime
from pyramid.httpexceptions import HTTPFound
from pyramid.response import FileIter

from substanced.util import get_oid

from dace.util import getSite
from dace.objectofcollaboration.principal.util import (
    has_role,
    has_any_roles,
    grant_roles,
    get_current)
from dace.interfaces import IEntity
from dace.processinstance.activity import (
    InfiniteCardinality,
    ActionType)
from deform_treepy.utilities.tree_utility import edit_keywords

from lac.content.interface import (
    ICreationCulturelleApplication, ISmartFolder,
    ISiteFolder, ISearchableEntity)
from lac.content.keyword import ROOT_TREE
from lac import _
from ..user_management.behaviors import global_user_processsecurity
from lac.core import access_action, serialize_roles
from lac.utilities.utils import (
    get_site_folder, to_localized_time)
from lac.mail import DEFAULT_SITE_MAILS
from lac import CLASSIFICATIONS
from lac.views.filter import find_entities
from lac.content.processes.services_processes.moderation_service import (
    is_site_moderator)


def get_access_key(obj):
    if 'published' in obj.state:
        return ['always']
    else:
        site = get_site_folder(True)
        return serialize_roles((('Owner', obj), ('SiteAdmin', site), 'Admin'))


def see_processsecurity_validation(process, context):
    site = get_site_folder(True)
    return 'published' in context.state or \
           has_any_roles(roles=('SiteAdmin', 'Admin'), root=site)\
           or has_role(role=('Owner', context))


@access_action(access_key=get_access_key)
class SeeSmartFolder(InfiniteCardinality):
    """SeeFile is the behavior allowing access to context"""
    title = _('Details')
    context = ISmartFolder
    actionType = ActionType.automatic
    processsecurity_validation = see_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def create_roles_validation(process, context):
    return has_role(role=('Member',))


class AddSmartFolder(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-folder-open'
    style_order = 0
    submission_title = _('Save')
    context = ICreationCulturelleApplication
    roles_validation = create_roles_validation

    def start(self, context, request, appstruct, **kw):
        new_smart_folder = appstruct['_object_data']
        context.addtoproperty('smart_folders', new_smart_folder)
        grant_roles(roles=(('Owner', new_smart_folder), ))
        new_smart_folder.setproperty('author', get_current())
        new_smart_folder.state = PersistentList(['private'])
        new_smart_folder.reindex()
        return {'newcontext': new_smart_folder}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(kw['newcontext'], "@@index"))


def createsub_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('SiteAdmin', 'Admin'), root=site)\
           or has_role(role=('Owner', context))


class AddSubSmartFolder(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-folder-open'
    style_order = 0
    submission_title = _('Save')
    context = ISmartFolder
    roles_validation = createsub_roles_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        new_smart_folder = appstruct['_object_data']
        root.addtoproperty('smart_folders', new_smart_folder)
        context.addtoproperty('children', new_smart_folder)
        grant_roles(roles=(('Owner', new_smart_folder), ))
        new_smart_folder.setproperty('author', get_current())
        new_smart_folder.state = PersistentList(['private'])
        new_smart_folder.filters = PersistentList(
            getattr(new_smart_folder, 'filters', []))
        new_smart_folder.reindex()
        return {'newcontext': new_smart_folder}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(kw['newcontext'], "@@index"))


def edit_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('SiteAdmin', 'Admin'), root=site) or \
        has_role(role=('Owner', context))


def edit_state_validation(process, context):
    site = get_site_folder(True)
    return 'private' in context.state or \
        has_any_roles(roles=('SiteAdmin', 'Admin'), root=site)


class EditSmartFolder(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-pencil'
    style_order = 1
    submission_title = _('Save')
    context = ISmartFolder
    roles_validation = edit_roles_validation
    state_validation = edit_state_validation

    def start(self, context, request, appstruct, **kw):
        context.filters = PersistentList(getattr(context, 'filters', []))
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class RemoveSmartFolder(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-trash'
    style_order = 2
    submission_title = _('Continue')
    context = ISmartFolder
    roles_validation = edit_roles_validation
    state_validation = edit_state_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        sub_folders = context.all_sub_folders()
        for sub_folder in sub_folders:
            root.delfromproperty('smart_folders', sub_folder)

        root.delfromproperty('smart_folders', context)
        return {}

    def redirect(self, context, request, **kw):
        root = getSite()
        return HTTPFound(request.resource_url(root, ""))


def admin_roles_validation(process, context):
    return has_role(role=('Admin',))


def siteadmin_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('SiteAdmin', 'Admin'), root=site)


def pub_state_validation(process, context):
    return 'private' in context.state


class PublishSmartFolder(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-share'
    style_order = 2
    submission_title = _('Continue')
    context = ISmartFolder
    roles_validation = siteadmin_roles_validation
    state_validation = pub_state_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['published'])
        filters = getattr(context, 'filters', [])
        for filter_ in filters:
            tree = filter_.get('metadata_filter', {}).get('tree', None)
            if tree:
                request.get_site_folder.merge_tree(tree)
                getSite().merge_tree(tree)

        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def withdraw_processsecurity_validation(process, context):
    return 'published' in context.state


class WithdrawSmartFolder(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-fast-backward'
    style_order = 2
    submission_title = _('Continue')
    context = ISmartFolder
    roles_validation = siteadmin_roles_validation
    processsecurity_validation = withdraw_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.state = PersistentList(['private'])
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def seesmartfolders_roles_validation(process, context):
    return has_role(role=('Member',))


class SeeSmartFolders(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-folder-open'
    style_order = 2
    context = ICreationCulturelleApplication
    roles_validation = seesmartfolders_roles_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context))


#Site folders

def get_access_key_site(obj):
    return serialize_roles((("SiteAdmin", obj),
                            'Admin'))


def see_processsecurity_validation(process, context):
    return has_role(role=('SiteAdmin', ), root=context) or \
           has_role(role=('Admin',))


@access_action(access_key=get_access_key_site)
class SeeSiteFolder(InfiniteCardinality):
    """SeeFile is the behavior allowing access to context"""
    title = _('Details')
    context = ISiteFolder
    actionType = ActionType.automatic
    processsecurity_validation = see_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class AddSiteFolder(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-globe'
    style_order = 0
    submission_title = _('Save')
    context = ICreationCulturelleApplication
    roles_validation = admin_roles_validation

    def start(self, context, request, appstruct, **kw):
        new_site_folder = appstruct['_object_data']
        templates = appstruct.get('mail_templates', [])
        for template in templates:
            template['title'] = DEFAULT_SITE_MAILS[template['mail_id']]['title']

        new_site_folder.mail_templates = templates
        context.addtoproperty('site_folders', new_site_folder)
        new_site_folder.state.append('published')
        new_site_folder.setproperty('author', get_current())
        new_site_folder.filters = PersistentList(
            getattr(new_site_folder, 'filters', []))
        new_site_folder.urls_ids = PersistentList(
            getattr(new_site_folder, 'urls_ids', []))
        new_site_folder.reindex()
        return {'newcontext': new_site_folder}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(kw['newcontext'], "@@configuresitefolder"))


class EditSiteFolder(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-pencil'
    style_order = 1
    submission_title = _('Save')
    context = ISiteFolder
    roles_validation = siteadmin_roles_validation

    def start(self, context, request, appstruct, **kw):
        site_folder = appstruct['_object_data']
        site_folder.modified_at = datetime.datetime.now(tz=pytz.UTC)
        site_folder.urls_ids = PersistentList(
            getattr(site_folder, 'urls_ids', []))
        site_folder.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class ConfigureSiteFolder(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-wrench'
    style_order = 2
    submission_title = _('Save')
    context = ISiteFolder
    roles_validation = siteadmin_roles_validation

    def start(self, context, request, appstruct, **kw):
        site_folder = appstruct['_object_data']
        site_folder.modified_at = datetime.datetime.now(tz=pytz.UTC)
        site_folder.filters = PersistentList(
            getattr(site_folder, 'filters', []))
        filters = getattr(site_folder, 'filters', [])
        root = getSite()
        for filter_ in filters:
            sources = filter_.get('other_filter', {}).get('sources', [])
            if sources and 'self' in sources:
                sources_ = list(sources)
                sources_.remove('self')
                sources_.append(str(get_oid(site_folder)))
                filter_['other_filter']['sources'] = list(set(sources_))

            tree = filter_.get('metadata_filter', {}).get('tree', None)
            if tree:
                site_folder.merge_tree(tree)
                root.merge_tree(tree)

        site_folder.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class RemoveSiteFolder(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-trash'
    style_order = 2
    submission_title = _('Continue')
    context = ISiteFolder
    roles_validation = admin_roles_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        root.delfromproperty('site_folders', context)
        return {}

    def redirect(self, context, request, **kw):
        root = getSite()
        return HTTPFound(request.resource_url(root, ""))


def seefolders_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('SiteAdmin', 'Admin'), root=site)


class SeeSiteFolders(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-globe'
    style_order = 2
    context = ICreationCulturelleApplication
    roles_validation = seefolders_roles_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context))


class FixAccessPerimeter(InfiniteCardinality):
    style = 'button'
    style_descriminator = 'footer-entity-action'
    style_picto = 'glyphicon glyphicon-eye-open'
    style_order = 0
    submission_title = _('Save')
    context = IEntity
    roles_validation = siteadmin_roles_validation

    def start(self, context, request, appstruct, **kw):
        access_control = appstruct['access_control']
        if 'self' in access_control:
            site = get_site_folder(True, request)
            if site:
                access_control = list(access_control)
                access_control.remove('self')
                access_control.append(get_oid(site))

        access_control = [get_oid(obj, obj) for obj in access_control]
        context.access_control = PersistentList(access_control)
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def managedup_processsecurity_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('SiteAdmin', 'Admin'), root=site)


class OrderSmartFolders(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'body-action'
    style_picto = 'glyphicon glyphicon-th-list'
    style_order = 8
    template = 'lac:views/templates/order_smart_folders.pt'
    submission_title = _('Save')
    context = ICreationCulturelleApplication
    processsecurity_validation = managedup_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        folders = appstruct['folders']
        site = get_site_folder(True)
        oid = get_oid(site)
        # current_order = sorted([f.get_order(oid) for f in folders])
        for index, folder in enumerate(folders):
            folder.set_order(oid, index)

        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@seesmartfolders"))


class OrderSubSmartFolders(OrderSmartFolders):
    context = ISmartFolder

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def extract_processsecurity_validation(process, context):
    site = get_site_folder(True)
    services = site.get_all_services(
        kinds=['extractionservice'], delegation=False)
    return services and\
        (has_any_roles(roles=('SiteAdmin', 'Reviewer', 'Admin'), root=site))


class Extract(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-export'
    style_order = 8
    submission_title = _('Continue')
    context = ICreationCulturelleApplication
    processsecurity_validation = extract_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        appstruct.pop('_csrf_token_')
        classifications_ids = appstruct.get('classifications', [])
        classifications = []
        source_class = None
        if classifications_ids:
            appstruct.pop('classifications')
            classifications = [CLASSIFICATIONS[fid] for fid
                               in classifications_ids]
            classifications.reverse()
            for classification in classifications:
                source_class = classification(source_class)

        objects = find_entities(user=user, include_site=True,
                                filters=appstruct['filters']
                                )
        default = datetime.datetime.now(tz=pytz.UTC)
        objects = sorted(objects,
                         key=lambda e: getattr(e, 'modified_at',
                                               default),
                         reverse=True)
        from lac.content.smart_folder import generate_search_smart_folder
        folder = generate_search_smart_folder('Extraction folder')
        folder.classifications = source_class
        odtfile = folder.classifications.extract(objects, request, folder,
                                                 template_type="extraction",
                                                 filters=appstruct['filters'])
        return {'file': odtfile, 'filters': appstruct['filters'], 'user': user}

    def redirect(self, context, request, **kw):
        filters = kw.get('filters', [])
        keywords = []
        if filters:
            keywords = list(filters[0].get(
                'metadata_filter', {}).get(
                'tree', {}).get(ROOT_TREE, {}).keys())

        keywords = '-'.join(keywords)
        user = kw.get('user', None)
        user_title = getattr(user, 'title', user.name)
        now = datetime.datetime.now()
        date = to_localized_time(now, request=request, translate=True)
        file_name = 'Extraction_{keywords}_{date}_{user}'.format(
            keywords=keywords, date=date, user=user_title)
        file_name = file_name.replace(' ', '-')
        odtfile = kw.get('file', '')
        response = request.response
        response.content_type = 'application/vnd.oasis.opendocument.text'
        response.content_disposition = 'inline; filename="{file_name}.odt"'.format(
            file_name=file_name)
        response.app_iter = FileIter(odtfile)
        return response


class ManageKeywords(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-tags'
    style_order = 8
    submission_title = _('Save')
    context = ICreationCulturelleApplication
    processsecurity_validation = managedup_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        source = appstruct['source']
        targets = appstruct['targets']
        root = getSite()
        edited = edit_keywords(targets, source, root.tree)
        if edited:
            root.tree = edited

        objects = find_entities(
            interfaces=[ISmartFolder])
        for folder in objects:
            filters = getattr(folder, 'filters', [])
            for filter_ in filters:
                tree = filter_.get('metadata_filter', {}).get('tree', None)
                if tree:
                    edited = edit_keywords(targets, source, tree)
                    if edited:
                        filter_['metadata_filter']['tree'] = edited

            folder.filters = PersistentList(filters)
            folder.reindex()

        objects = find_entities(interfaces=[ISearchableEntity],
                                keywords=[kw.lower() for kw in targets])
        for obj in objects:
            edited = edit_keywords(targets, source, obj.tree)
            if edited:
                obj.tree = edited
                obj.reindex()

        objects = find_entities(interfaces=[ISiteFolder])
        for folder in objects:
            edited = edit_keywords(targets, source, folder.tree)
            if edited:
                folder.tree = edited

            filters = getattr(folder, 'filters', [])
            for filter_ in filters:
                tree = filter_.get('metadata_filter', {}).get('tree', None)
                if tree:
                    edited = edit_keywords(targets, source, tree)
                    if edited:
                        filter_['metadata_filter']['tree'] = edited

            folder.filters = PersistentList(filters)
            folder.reindex()

        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, ""))

#TODO behaviors
