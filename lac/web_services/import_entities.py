
# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi, Sophie Jazwiecki

import colander
import json
import urllib
import transaction
from persistent.list import PersistentList
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from substanced.util import get_oid

from dace.objectofcollaboration.principal.util import has_role
from dace.util import getSite, get_obj
from dace.processinstance.core import (
    Behavior, ValidationError, Validator)
from dace.util import find_catalog
from pontus.form import FormView
from pontus.widget import FileWidget
from pontus.file import ObjectData, File
from pontus.view import BasicView

from lac import _, log
from lac.utilities.data_manager import (
    create_object,
    merge_venues,
    merge_artists)
from lac.content.keyword import ROOT_TREE
from lac.content.service import IMPORT_SOURCES
from lac.views.admin_process.fix_access_perimeter import (
    AccessPerimeterSchema)
from lac.content.processes.artist_management.behaviors import (
    publish_artist)
from lac.content.processes.venue_management.behaviors import (
    publish_venue)
from lac.utilities.utils import get_site_folder


NB_AFTER_COMMIT = 200


def _get_obj(site_str):
    try:
        return get_obj(int(site_str))
    except:
        return None


def _get_oid(obj):
    try:
        return get_oid(obj)
    except:
        return None


def get_application_sites(sites, root, current_site):
    result = sites
    if 'all' in result:
        all_sites = root.site_folders
        result.extend(all_sites)
        result.remove('all')
        result = list(set(result))

    if 'self' in result:
        result.append(current_site)
        result.remove('self')
        result = list(set(result))

    return result


def get_new_entities(entities):
    entities_with_ids = [entity for entity in entities
                         if entity.get('source_data', {}).get('id', None)]
    entities_without_ids = [entity for entity in entities
                            if entity.get('source_data', {}).get('id', None) is None]
    ids = {str(entity['source_data']['id'] + '_' + entity['source_data']['source_id']): entity
           for entity in entities_with_ids}
    lac_catalog = find_catalog('lac')
    object_id_index = lac_catalog['object_id']
    # TODO really needed to wake up objects?
    current_objects = list(object_id_index.any(list(ids.keys())).execute())
    current_objects_ids = [str(getattr(entity, 'object_id',
                               getattr(entity, '__oid__', None)))
                           for entity in current_objects]
    #recuperate new entities
    entities_to_import = [entity for key, entity in ids.items()
                          if key not in current_objects_ids]
    entities_to_import.extend(entities_without_ids)
    return entities_to_import, current_objects


def get_valid_sites(root):
    """Return sites by service if sites have
       recorded the import service."""

    sites = root.site_folders
    valid_sites = {}
    for site in sites:
        valid_sites[site] = []
        importservices = site.get_services('importservice')
        if importservices:
            for service in importservices:
                if service.is_valid(site, None):
                    valid_sites[site].append(service)

    result = {}
    for provider in IMPORT_SOURCES:
        result[provider] = []
        for site in valid_sites:
            if any(provider in getattr(service, 'sources', [])
                   for service in valid_sites[site]):
                result[provider].append(get_oid(site))

        result[provider] = list(set(result[provider]))

    return result


def get_access_control(entity, sites=None, access_control=None):
    """The access_control getter.
       'entity' is a dict contains data,
       'sites' site ids by service,
       'access_control' site ids if not sites"""

    source_id = entity.get('source_data', {}).get('source_id', None)
    if not sites and not access_control:
        raise ValidationError(msg=_("You have to create services first"))

    if access_control is None:
        access_control = PersistentList(list(sites[source_id]))\
            if sites.get(source_id, None) else None
    else:
        access_control = [get_oid(site, site) for site in access_control]

    return access_control


def cultural_events_factory(entity, state, root,
                            sites=None, access_control=None):
    """The cultural event factory. Add a cultural event to the 'root'.
       'entity' is a dict contains data,
       'state' the state of the added cultural event,
       'sites' site ids by service,
       'access_control' site ids if not sites"""

    access_control = get_access_control(entity, sites, access_control)
    if access_control:
        if 'tree' in entity and ROOT_TREE not in entity['tree']:
            entity['tree'] = {ROOT_TREE: entity['tree']}

        obj = create_object('cultural_event', entity)
        obj.state.append(state)
        obj.access_control = PersistentList(access_control)
        root.addtoproperty('cultural_events', obj)
        if state == 'published':
            tree = getattr(obj, '_tree', None)
            if tree:
                sites = [_get_obj(s) for s in access_control]
                root.merge_tree(tree)
                for site in [s for s in sites if s]:
                    site.merge_tree(tree)

            for artist in obj.artists:
                publish_artist(artist)

            for schedule in obj.schedules:
                publish_venue(schedule.venue)

        obj.reindex()


def reviews_factory(entity, state, root,
                    sites=None, access_control=None):
    """The review factory. Add a review to the 'root'.
       'entity' is a dict contains data,
       'state' the state of the added review,
       'sites' site ids by service,
       'access_control' site ids if not sites"""

    access_control = get_access_control(entity, sites, access_control)
    if access_control:
        if 'tree' in entity and ROOT_TREE not in entity['tree']:
            entity['tree'] = {ROOT_TREE: entity['tree']}

        obj = create_object('review', entity)
        obj.state.append(state)
        obj.access_control = PersistentList(access_control)
        root.addtoproperty('reviews', obj)
        if state == 'published':
            tree = getattr(obj, '_tree', None)
            if tree:
                sites = [_get_obj(s) for s in access_control]
                root.merge_tree(tree)
                for site in [s for s in sites if s]:
                    site.merge_tree(tree)

            for artist in obj.artists:
                publish_artist(artist)

        obj.reindex()


def interviews_factory(entity, state, root,
                    sites=None, access_control=None):
    """The review factory. Add a review to the 'root'.
       'entity' is a dict contains data,
       'state' the state of the added interview,
       'sites' site ids by service,
       'access_control' site ids if not sites"""

    access_control = get_access_control(entity, sites, access_control)
    if access_control:
        if 'tree' in entity and ROOT_TREE not in entity['tree']:
            entity['tree'] = {ROOT_TREE: entity['tree']}

        obj = create_object('interview', entity)
        obj.state.append(state)
        obj.access_control = PersistentList(access_control)
        root.addtoproperty('reviews', obj)
        if state == 'published':
            tree = getattr(obj, '_tree', None)
            if tree:
                sites = [_get_obj(s) for s in access_control]
                root.merge_tree(tree)
                for site in [s for s in sites if s]:
                    site.merge_tree(tree)

            for artist in obj.artists:
                publish_artist(artist)

        obj.reindex()


def cinema_reviews_factory(entity, state, root,
                           sites=None, access_control=None):
    """The cinema review factory. Add a cinema review to the 'root'.
       'entity' is a dict contains data,
       'state' the state of the added cinema review,
       'sites' site ids by service,
       'access_control' site ids if not sites"""

    access_control = get_access_control(entity, sites, access_control)
    if access_control:
        if 'tree' in entity and ROOT_TREE not in entity['tree']:
            entity['tree'] = {ROOT_TREE: entity['tree']}

        obj = create_object('cinema_review', entity)
        obj.state.append(state)
        obj.access_control = PersistentList(access_control)
        root.addtoproperty('reviews', obj)
        if state == 'published':
            tree = getattr(obj, '_tree', None)
            if tree:
                sites = [_get_obj(s) for s in access_control]
                root.merge_tree(tree)
                for site in [s for s in sites if s]:
                    site.merge_tree(tree)

            for artist in obj.artists:
                publish_artist(artist)

            for director in obj.directors:
                publish_artist(director)

        obj.reindex()


def venues_factory(entity, state, root,
                   sites=None, access_control=None):
    """The venue factory. Add a venue to the 'root'.
       'entity' is a dict contains data,
       'state' the state of the added cultural event,
       'sites' site ids by service,
       'access_control' site ids if not sites"""

    obj = create_object('venue', entity)
    new_objs = merge_venues([obj])
    if new_objs and obj in new_objs:
        obj.state = PersistentList([state])
        root.addtoproperty('venues', obj)
        obj.reindex()


def artists_factory(entity, state, root,
                    sites=None, access_control=None):
    """The artist factory. Add a artist to the 'root'.
       'entity' is a dict contains data,
       'state' the state of the added cultural event,
       'sites' site ids by service,
       'access_control' site ids if not sites"""

    obj = create_object('artist', entity)
    new_objs = merge_artists([obj])
    if new_objs and obj in new_objs:
        obj.state = PersistentList([state])
        root.addtoproperty('artists', obj)
        obj.reindex()


def smartfolder_factory(entity, state, root,
                        sites=None, access_control=None):
    """The smartfolder factory. Add a smartfolder to the 'root'.
       'entity' is a dict contains data,
       'state' the state of the added cultural event,
       'sites' site ids by service,
       'access_control' site ids if not sites"""
    access_control = get_access_control(entity, sites, access_control)
    obj = create_object('smartfolder', entity)
    if obj:
        folder_filters_md = [f.get('metada_filter')
                             for f in obj.filters
                             if 'metada_filter' in f and
                             'tree' in f['metada_filter']]
        for filter_ in folder_filters_md:
            if ROOT_TREE not in filter_['tree']:
                filter_['tree'] = {ROOT_TREE: filter_['tree']}

        obj.state = PersistentList([state])
        root.addtoproperty('smart_folders', obj)
        obj.access_control = PersistentList(access_control)
        for subfolder in obj.all_sub_folders():
            subfolder.state = PersistentList([state])

        if state == 'published':
            sites = [_get_obj(s) for s in access_control]
            for filter_ in folder_filters_md:
                tree = filter_.get('tree')
                root.merge_tree(tree)
                for site in [s for s in sites if s]:
                    site.merge_tree(tree)

        obj.reindex()


FACTORIES = {'cultural_event': cultural_events_factory,
             'review': reviews_factory,
             'cinema_review': cinema_reviews_factory,
             'interview': interviews_factory,
             'venue': venues_factory,
             'artist': artists_factory,
             'smartfolder': smartfolder_factory}


class SendValidator(Validator):
    """The validor for the Send behavior"""

    @classmethod
    def validate(cls, context, request, **kw):
        from pyramid.security import authenticated_userid
        if has_role(role=('Admin',)) or \
           authenticated_userid(request) == 'admin':
            if not request.user:
                request.user = request.root['principals']['users']['admin']

            return True

        raise ValidationError(msg=_("Permission denied"))


class Send(Behavior):
    """The behavior to be executed for import entities form"""

    behavior_id = "send"
    title = _("Send")
    description = ""

    @classmethod
    def get_validator(cls, **kw):
        return SendValidator

    def start(self, context, request, appstruct, **kw):
        """Load entities from the selected json file"""
        root = getSite()
        current_site = get_site_folder(True, request)
        entities = appstruct.get('entities')
        entities_file = entities['_object_data'].fp
        entities_str = entities_file.readall().decode('utf8')
        #Load entities
        entities_list = json.loads(entities_str)
        #Recuperate the access control (sites where entities will be displayed)
        new_entities, current_objects = get_new_entities(entities_list)
        access_control = list(appstruct.get('access_control', None))
        access_control = get_application_sites(
            access_control, root, current_site)
        for object_ in current_objects:
            obj_access_control = getattr(object_, 'access_control', [])
            if obj_access_control and 'all' not in obj_access_control:
                obj_access_control.extend([get_oid(s) for s in access_control])
                object_.access_control = PersistentList(set(obj_access_control))
                object_.reindex()

        len_entities = str(len(new_entities))
        for index, entity in enumerate(new_entities):
            #recuperate the type of the entitie
            entity_type = entity.pop('type')
            #recuperate the factory
            factory = FACTORIES.get(entity_type, None)
            if factory:
                #add the entitie
                try:
                    factory(entity, 'published',
                            root, access_control=access_control)

                    log.info(str(index) + "/" + len_entities)
                except Exception as error:
                    log.warning(error)

            if index % NB_AFTER_COMMIT == 0:
                log.info("**** Commit ****")
                transaction.commit()

        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, ""))


class ImportEntitiesJsonSchema(AccessPerimeterSchema):
    """Schema for import entities form"""

    entities = colander.SchemaNode(
        ObjectData(File),
        widget=FileWidget(file_extensions=['json']),
        title=_('Entities'),
        description=_("Only JSON files are supported."),
        )


@view_config(name='import',
             renderer='lac:web_services/templates/grid.pt',
             layout='web_services_layout')
class ImportEntitiesJson(FormView):

    """Import entities form."""

    title = _('Import entities')
    name = 'import'
    schema = ImportEntitiesJsonSchema()
    behaviors = [Send]


@view_config(name='import_url',
             renderer='lac:web_services/templates/grid.pt',
             layout='web_services_layout')
class ImportEntitiesURL(BasicView):

    """Find entities form. Import entities from import services"""

    title = _('Import entities from url')
    name = 'import_url'
    template = 'lac:web_services/templates/import_url.pt'
    validators = [Send.get_validator()]

    def update(self):
        root = getSite()
        valid_sites = get_valid_sites(root)
        #recuperate the source url: json file (see servicies: digitick...)
        source = self.params('source')
        if source:
            entities_file = urllib.request.urlopen(source)
            entities_str = entities_file.read().decode('utf8')
            #load the json file (all entities)
            all_imported_entities = json.loads(entities_str)
            #recuperate new entities
            entities_to_import, current_objects = get_new_entities(all_imported_entities)
            len_entities = str(len(entities_to_import))
            for index, entity in enumerate(entities_to_import):
                #recuperate the type of the entitie
                entity_type = entity.pop('type')
                #recuperate the factory
                factory = FACTORIES.get(entity_type, None)
                if factory:
                    #add the entitie
                    try:
                        factory(entity, 'submitted',
                                root, sites=valid_sites)
                        log.info(str(index) + "/" + len_entities)
                    except Exception as error:
                        log.warning(error)

                if index % NB_AFTER_COMMIT == 0:
                    log.info("**** Commit ****")
                    transaction.commit()

        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result
