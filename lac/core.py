# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
import venusian
import deform
import json
import datetime
import pytz
from persistent.list import PersistentList
from persistent.dict import PersistentDict
from zope.interface import implementer
from pyramid.threadlocal import get_current_registry

from substanced.util import get_oid

from dace.objectofcollaboration.entity import Entity
from dace.descriptors import (
    SharedUniqueProperty,
    SharedMultipleProperty,
    CompositeUniqueProperty,
    CompositeMultipleProperty
    )
from dace.objectofcollaboration.principal.util import (
    has_role, get_current, has_any_roles, get_access_keys)
from dace.objectofcollaboration.principal.role import DACE_ROLES
from dace.util import getSite, get_obj
from pontus.schema import Schema, omit, select
from pontus.core import VisualisableElementSchema, VisualisableElement
from pontus.widget import (
    AjaxSelect2Widget,
    FileWidget,
    SimpleMappingWidget,
    SequenceWidget)
from pontus.file import Image, ObjectData as ObjectDataOrigin
from pontus.form import FileUploadTempStore
from deform_treepy.utilities.tree_utility import (
    get_keywords_by_level,
    tree_min_len)
from deform_treepy.widget import (
    KeywordsTreeWidget,
    DictSchemaType)

from lac import _, log, ACCESS_ACTIONS
from lac.views.widget import SimpleMappingtWidget
from lac.content.interface import (
    ISearchableEntity,
    IFile,
    IDuplicableEntity,
    IBaseReview,
    IAdvertising,
    ILabel,
    IParticipativeEntity)
from lac.views.widget import (
    DateIcalWidget,
    RichTextWidget)
from lac.content.keyword import (
    DEFAULT_TREE, DEFAULT_TREE_LEN, ROOT_TREE)
from lac.utilities.utils import (
    synchronize_tree, get_site_folder,
    dates, html_article_to_text, deepcopy)
from lac.utilities import french_dates_parser as Parser


BATCH_DEFAULT_SIZE = 30


ADVERTISING_CONTAINERS = {}


SEARCHABLE_CONTENTS = {}


SITE_WIDGETS = {}


SERVICES = ['moderation', 'sellingtickets', 'importservice']


IMPORT_SOURCES = {'digitick':
    {
        'title': 'Digitick',
        'icon': 'lac:static/images/digitick32.png',
        'url': 'http://www.digitick.com'
    }
}


SERVICES_DEFINITION = {}

SOCIAL_APPLICATIONS = {}


def object_set_access_control(accessibility, context, site):
    site_oid = get_oid(site)
    access_control = getattr(context, 'access_control', ['all'])
    if accessibility:
        context.access_control = PersistentList([site_oid])
    else:
        if len(access_control) == 1 and site_oid in access_control:
            context.access_control = PersistentList(['all'])


class service_definition(object):

    def __init__(self, direct=False, **kw):
        self.direct = direct
        self.kw = kw

    def __call__(self, wrapped):
        def callback(scanner, name, ob):
            if self.direct:
                component = ob
            else:
                component = ob(**self.kw)

            SERVICES_DEFINITION[component.service_id] = component

        venusian.attach(wrapped, callback)
        return wrapped


class social_application(object):

    def __init__(self, schema, attributes):
        self.schema = schema
        self.attributes = attributes

    def __call__(self, wrapped):
        def callback(scanner, name, ob):
            SOCIAL_APPLICATIONS[ob] = select(
                self.schema(editable=True, factory=ob), self.attributes)

        venusian.attach(wrapped, callback)
        return wrapped


class advertising_banner_config(object):
    """ A function, class or method decorator which allows a
    developer to create advertising banner registrations.

    Advertising banner is a panel. See pyramid_layout.panel_config.
    """
    def __init__(self, name='', context=None, renderer=None, attr=None):
        self.name = name
        self.context = context
        self.renderer = renderer
        self.attr = attr

    def __call__(self, wrapped):
        settings = self.__dict__.copy()

        def callback(context, name, ob):
            config = context.config.with_package(info.module)
            config.add_panel(panel=ob, **settings)
            ADVERTISING_CONTAINERS[self.name] = {'title': ob.title,
                                                 'description': ob.description,
                                                 'order': ob.order,
                                                 'validator': ob.validator,
                                                 'tags': ob.tags
                                                 #TODO add validator ob.validator
                                                 }

        info = venusian.attach(wrapped, callback, category='pyramid_layout')

        if info.scope == 'class':
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if settings['attr'] is None:
                settings['attr'] = wrapped.__name__

        settings['_info'] = info.codeinfo # fbo "action_method"
        return wrapped


class site_widget_config(object):
    """ A function, class or method decorator which allows a
    developer to create advertising banner registrations.

    Advertising banner is a panel. See pyramid_layout.panel_config.
    """
    def __init__(self, name, title, validator=None, renderer=None):
        self.name = name
        self.title = title
        self.renderer = renderer
        self.validator = validator

    def __call__(self, wrapped):
        def callback(scanner, name, ob):
            ob.widget_name = self.name
            ob.widget_validator = self.validator
            old_call = ob.__call__
            def __call__(self):
                if not self.widget_validator():
                    return {'condition': False}

                result = old_call(self)
                result.update({'condition': True})
                return result

            ob.__call__ = __call__
            if self.name in SITE_WIDGETS:
                SITE_WIDGETS[self.name]['views'].append(ob)
            else:
                SITE_WIDGETS[self.name] = {
                    'views': [ob],
                    'renderer': self.renderer,
                    'title': self.title,
                    'validator': self.validator
                }

        venusian.attach(wrapped, callback, category='site_widget')
        return wrapped


class access_action(object):
    """ Decorator for lac access actions.
    An access action allows to view an object"""

    def __init__(self, access_key=None):
        self.access_key = access_key

    def __call__(self, wrapped):
        def callback(scanner, name, ob):
            if ob.context in ACCESS_ACTIONS:
                ACCESS_ACTIONS[ob.context].append({'action': ob,
                                                  'access_key': self.access_key})
            else:
                ACCESS_ACTIONS[ob.context] = [{'action': ob,
                                              'access_key': self.access_key}]

        venusian.attach(wrapped, callback)
        return wrapped


def can_access(user, context, request=None, root=None):
    """ Return 'True' if the user can access to the context"""
    declared = context.__provides__.declared[0]
    for data in ACCESS_ACTIONS.get(declared, []):
        if data['action'].processsecurity_validation(None, context):
            return True

    return False


_marker = object()


def serialize_roles(roles, root=None):
    result = []
    principal_root = getSite()
    if principal_root is None:
        return []

    if root is None:
        root = principal_root

    root_oid = str(get_oid(root, ''))
    principal_root_oid = str(get_oid(principal_root, ''))
    for role in roles:
        if isinstance(role, tuple):
            obj_oid = str(get_oid(role[1], ''))
            result.append((role[0]+'_'+obj_oid).lower())
            superiors = getattr(DACE_ROLES.get(role[0], _marker),
                                'all_superiors', [])
            result.extend([(r.name+'_'+obj_oid).lower()\
                           for r in superiors])
        else:
            result.append(role.lower()+'_'+root_oid)
            superiors = getattr(DACE_ROLES.get(role, _marker),
                                'all_superiors', [])
            result.extend([(r.name+'_'+root_oid).lower() for r in\
                           superiors])

        for superior in superiors:
            if superior.name == 'Admin':
                result.append('admin_'+principal_root_oid)
                break

    return list(set(result))


def generate_access_keys(user, root, site):
    excluded_sites = list(root.site_folders)
    root_oid = str(get_oid(root))
    if site in excluded_sites:
        excluded_sites.remove(site)

    excluded_sites_ids = [get_oid(ex_site)
                          for ex_site in excluded_sites]
    access_keys = get_access_keys(
        user, root=root, to_exclude=excluded_sites_ids)
    root_keys = [a for a in access_keys if a.endswith(root_oid)]
    root_roles = [(a, a.replace('_'+root_oid, '')) for a in root_keys]
    local_keys = list(set(access_keys) - set(root_keys))

    def is_valid(role, local_keys):
        return role == 'admin' or\
            any(a.startswith(role)
                for a in local_keys)

    valid_root_keys = [a for a, role in root_roles 
                       if is_valid(role, local_keys)]
    valid_access_keys = local_keys
    valid_access_keys.extend(valid_root_keys)
    return valid_access_keys


class Product(Entity):

    order = SharedUniqueProperty('order', 'products')

    def __init__(self, **kwargs):
        super(Product, self).__init__(**kwargs)
        self.source_site = get_oid(get_site_folder(True),
                                   None)

    def get_price(self):
        return 0

    @property
    def price_str(self):
        price = self.get_price()
        return str(price) + '€'


class ServiceableEntity(Entity):

    services = SharedMultipleProperty('services', 'perimeter')

    def __init__(self, **kwargs):
        super(ServiceableEntity, self).__init__(**kwargs)

    def get_services(self, kind=None, user=None):
        services = self.services
        if user:
            services = [s for s in self.services if
                        can_access(user, s)]

        if not services or kind is None:
            return services

        # registry_content = get_current_registry().content
        return [s for s in services if s.definition.service_id == kind]

    def get_all_services(self, context=None, user=None,
                         site=None, kinds=None,
                         validate=True, delegation=True):
        if user is None:
            user = get_current()

        if site is None:
            site = get_site_folder(True)

        if context is None:
            context = self

        if kinds is None:
            kinds = SERVICES

        services = {}
        for service in kinds:
            services[service] = self.get_services(service)

        result = {}
        for service, items in services.items():
            result[service] = []
            for item in items:
                if context is item.perimeter and \
                   (not validate or (validate and item.is_valid(context, user))) \
                   and (not delegation or (delegation and item.delegated_to(user))):
                    result[service].append(item)

            result[service] = list(set(result[service]))

        return {service: value for service, value in result.items() if value}


@colander.deferred
def keyword_widget(node, kw):
    request = node.bindings['request']
    site = request.get_site_folder
    can_create = 0
    if has_role(role=('Member', )):
        can_create = 1
    if has_any_roles(roles=('Admin', ('SiteAdmin', site))):
        can_create = 0

    levels = site.get_tree_nodes_by_level()
    return KeywordsTreeWidget(
        min_len=2,
        max_len=DEFAULT_TREE_LEN,
        can_create=can_create,
        levels=levels)


@colander.deferred
def keywords_validator(node, kw):
    if DEFAULT_TREE == kw or tree_min_len(kw) < 3:
        raise colander.Invalid(
            node, _('Minimum one categorie required. Please specify a second keyword level for each category chosen.'))


def get_file_widget(**kargs):
    @colander.deferred
    def file_widget(node, kw):
        request = node.bindings['request']
        tmpstore = FileUploadTempStore(request)
        return FileWidget(
            tmpstore=tmpstore,
            **kargs
            )

    return file_widget


class LabelSchema(VisualisableElementSchema):

    picture = colander.SchemaNode(
        ObjectDataOrigin(Image),
        widget=get_file_widget(file_type=['image']),
        title=_('Picture'),
        )


@implementer(ILabel)
class Label(VisualisableElement, Entity):

    picture = CompositeUniqueProperty('picture')

    def __init__(self, **kwargs):
        super(Label, self).__init__(**kwargs)

    @property
    def relevant_data(self):
        return [getattr(self, 'title', ''),
                getattr(self, 'description', '')]


@colander.deferred
def dates_validator(node, kw):
    def _dates_validator(node, value):
        try:
            if Parser.getDatesFromSeances(value) is None:
                raise colander.Invalid(node, _('Not valid value'))
        except AttributeError as e:
            raise colander.Invalid(node, e.args[0])

    return _dates_validator


@colander.deferred
def connect_to_choices(node, kw):
    """Country must be in the select tag for the initialization"""
    context = node.bindings['context']
    request = node.bindings['request']
    values = []
    ajax_url = request.resource_url(context,
                                    '@@creationculturelapi',
                                    query={'op': 'find_entity'})

    def title_getter(oid):
        try:
            obj = get_obj(int(oid), None)
            if obj:
                return obj.title
            else:
                return oid
        except Exception as e:
            log.warning(e)
            return oid

    return AjaxSelect2Widget(
        values=values,
        ajax_url=ajax_url,
        multiple=True,
        title_getter=title_getter,
        ajax_item_template='formatReview'
        )


@colander.deferred
def release_date_default(node, kw):
    context = node.bindings['context']
    if isinstance(context, SearchableEntity):
        return getattr(context, 'release_date', context.modified_at)

    return datetime.datetime.now(tz=pytz.UTC)


@colander.deferred
def default_accessibility(node, kw):
    context = node.bindings['context']
    access_control = getattr(context, 'access_control', ['all'])
    return False if 'all' in access_control else True


@colander.deferred
def labels_choices(node, kw):
    """Country must be in the select tag for the initialization"""
    context = node.bindings['context']
    request = node.bindings['request']
    values = []
    ajax_url = request.resource_url(context,
                                    '@@creationculturelapi',
                                    query={'op': 'find_labels'})

    def title_getter(oid):
        try:
            obj = get_obj(int(oid), None)
            if obj:
                return obj.title
            else:
                return oid
        except Exception as e:
            log.warning(e)
            return oid

    return AjaxSelect2Widget(
        values=values,
        ajax_url=ajax_url,
        multiple=True,
        title_getter=title_getter,
        ajax_item_template='formatLabel'
        )


class LabelsSchema(Schema):

    labels = colander.SchemaNode(
        colander.Set(),
        widget=labels_choices,
        title=_('Labels'),
        description=_('You can add labels to this object.'),
        default=[],
        missing=[]
        )

    new_labels = colander.SchemaNode(
        colander.Sequence(),
        omit(select(LabelSchema(
            name='new_label',
            factory=Label,
            editable=True,
            widget=SimpleMappingWidget(
               css_class='label-well object-well default-well')),
            ['title', 'picture']),
        ['_csrf_token_']),
        widget=SequenceWidget(
            add_subitem_text_template=_('Add a new label')),
        title=_('New labels'),
        )


class MetadataSchema(Schema):

    visibility_dates = colander.SchemaNode(
        colander.String(),
        validator=dates_validator,
        widget=DateIcalWidget(),
        title=_('Visibility dates'),
        missing=''
        )

    release_date = colander.SchemaNode(
        colander.DateTime(),
        title=_('Release date'),
        default=release_date_default
        )

    accessibility = colander.SchemaNode(
        colander.Boolean(),
        widget=deform.widget.CheckboxWidget(),
        label=_('Make accessible only on this site'),
        title='',
        default=default_accessibility,
        missing=False
        )

    connections_to = colander.SchemaNode(
        colander.Set(),
        widget=connect_to_choices,
        title=_('Connect to'),
        description=_('You can connect this object to other objects.'),
        default=[],
        missing=[]
        )

    object_labels = omit(LabelsSchema(widget=SimpleMappingWidget(
                                   css_class='object-well default-well')),
                  ["_csrf_token_"])


class ObjectData(ObjectDataOrigin):

    def clean_cstruct(self, node, cstruct):
        result, appstruct, hasevalue = super(ObjectData, self)\
            .clean_cstruct(node, cstruct)
        if 'metadata' not in result:
            return result, appstruct, hasevalue

        metadata = result.pop('metadata', {})
        result.update(metadata)
        return result, appstruct, hasevalue


class SearchableEntitySchema(Schema):
    typ_factory = ObjectData

    tree = colander.SchemaNode(
        typ=DictSchemaType(),
        validator=colander.All(keywords_validator),
        widget=keyword_widget,
        default=DEFAULT_TREE,
        title=_('Categories'),
        description=_('Indicate the category of the event. Please specify a second keyword level for each category chosen.')
        )

    metadata = omit(MetadataSchema(widget=SimpleMappingtWidget(
                                mapping_css_class='controled-form'
                                                  ' object-well default-well hide-bloc',
                                control_css_class='alert alert-success',
                                ajax=True,
                                activator_css_class="glyphicon glyphicon-cog",
                                activator_title=_('Manage metadata'))),
                        ["_csrf_token_"])

    def deserialize(self, cstruct=colander.null):
        appstruct = super(SearchableEntitySchema, self).deserialize(cstruct)
        if 'metadata' not in appstruct:
            return appstruct

        metadata = appstruct.pop('metadata', {})
        appstruct.update(metadata)
        return appstruct


@implementer(ISearchableEntity)
class SearchableEntity(ServiceableEntity):
    """ A Searchable entity is an entity that can be searched"""

    icon = 'glyphicon glyphicon-question-sign'
    templates = {'default': 'lac:views/templates/default_result.pt',
                 'bloc': 'lac:views/templates/default_result_bloc.pt',
                 'extraction': 'lac:views/templates/extraction/default_result.pt'}
    tree = synchronize_tree()
    type_title = ''
    files = CompositeMultipleProperty('files')
    connections_from = SharedMultipleProperty(
        'connections_from', 'connections_to')
    connections_to = SharedMultipleProperty(
        'connections_to', 'connections_from')
    visibility_dates = dates('visibility_dates')
    labels = SharedMultipleProperty('labels')

    def __init__(self, **kwargs):
        super(SearchableEntity, self).__init__(**kwargs)
        self._tree = PersistentDict()
        self.keywords = PersistentList()
        self.set_data(kwargs)
        self.source_site = get_oid(get_site_folder(True),
                                   None)
        self._keywords_ = []
        self._init_keywords()

    def __setattr__(self, name, value):
        super(SearchableEntity, self).__setattr__(name, value)
        if name == 'description':
            self._init_presentation_text()

    @property
    def object_labels(self):
        return {'labels': self.labels}

    @property
    def metadata(self):
        return self.get_data(omit(MetadataSchema(),
                                 '_csrf_token_'))

    @property
    def is_published(self):
        return 'published' in self.state

    @property
    def object_id(self):
        source_data = getattr(self, 'source_data', {})
        obj_id = source_data.get('id', '') + '_' +\
            source_data.get('source_id', '')
        if obj_id == '_':
            obj_id = str(getattr(self, '__oid__', None))+'_lac'

        return obj_id

    @property
    def json_tree(self):
        return json.dumps(dict(self.tree))

    @property
    def is_imported(self):
        source_id = getattr(self, 'source_data', {}).get('source_id', None)
        return True if source_id and source_id in list(IMPORT_SOURCES.keys())\
               else False

    @property
    def relevant_data(self):
        return [getattr(self, 'title', ''),
                getattr(self, 'description', ''),
                ', '.join(self.keywords)]

    @property
    def sections(self):
        tree = dict(self.get_normalized_tree())
        levels = get_keywords_by_level(tree, ROOT_TREE)
        if len(levels) >= 2:
            return sorted(levels[1])

        return []

    @property
    def substitutions(self):
        return [self]

    def _init_presentation_text(self):
        pass

    def _init_keywords(self):
        pass

    def get_all_keywords(self):
        return self.keywords

    def get_more_contents_criteria(self):
        "return specific query, filter values"
        keywords = list(self.keywords)
        root_tree = ROOT_TREE.lower()
        if root_tree in keywords:
            keywords.remove(root_tree)

        return None, {'keywords': keywords}

    def get_release_date(self):
        return getattr(self, 'release_date', self.modified_at)

    def presentation_text(self, nb_characters=400):
        return getattr(self, 'description', "")[:nb_characters]+'...'

    def get_normalized_tree(self, type_='out'):
        site = get_site_folder(True)
        return site.get_normalized_tree(getattr(self, 'tree', {}), type_)

    def get_visibility_filter(self):
        registry = get_current_registry()
        return {
            'metadata_filter': {
                'tree': deepcopy(self.tree),
                'content_types': [registry.content.typeof(self)],
                'states': list(getattr(self, 'state', []))
            }
        }

    def set_metadata(self, appstruct):
        if 'site' not in appstruct:
            site = get_site_folder(True)

        if 'accessibility' in appstruct:
            object_set_access_control(appstruct.get('accessibility'), self, site)
            appstruct.pop('accessibility')

        data = {}
        for key in MetadataSchema():
            name = key.name
            if name in appstruct:
                data[name] = appstruct.pop(name)

        if 'object_labels' in data:
            new_labels = [label['_object_data'] for label
                          in data['object_labels']['new_labels']]
            all_labels = []
            if new_labels:
                root = site.__parent__
                for label in new_labels:
                    root.addtoproperty('labels', label)
                    all_labels.append(label)

            all_labels.extend(data['object_labels']['labels'])
            data['labels'] = all_labels
            data.pop('object_labels')

        self.set_data(data)
        self.release_date = getattr(
            self, 'release_date', self.created_at).replace(
            tzinfo=pytz.UTC)

    def labels_data(self, site):
        labels = getattr(self, 'labels', [])
        labels_data = [{'title': l.title,
                        'img': l.picture.url} for l in labels]
        site_oid = get_oid(site)
        if site_oid != self.source_site:
            orig_site = get_obj(self.source_site)
            if orig_site.favicon:
                labels_data.append({'title': orig_site.title,
                                    'img': orig_site.favicon.url})

        return labels_data


@implementer(IDuplicableEntity)
class DuplicableEntity(Entity):
    """ A Duplicable entity is an entity that can be duplicated"""

    original = SharedUniqueProperty('original', 'branches')
    branches = SharedMultipleProperty('branches', 'original')


@implementer(IParticipativeEntity)
class ParticipativeEntity(Entity):
    """ A Participative entity is an entity that can be improved"""

    contributors = SharedMultipleProperty('contributors', 'contributions')

    def add_contributors(self, contributors):
        for contributor in contributors:
            if contributor not in self.contributors:
                self.addtoproperty('contributors', contributor)

    def replace_by(self, source):
        pass


class FileSchema(VisualisableElementSchema, SearchableEntitySchema):

    text = colander.SchemaNode(
        colander.String(),
        widget=RichTextWidget(),
        title=_("Text")
        )


@implementer(IFile)
class FileEntity(SearchableEntity):
    """ A file entity is an entity that can be searched"""

    icon = 'lac-icon icon-file'
    templates = {'default': 'lac:views/templates/file_result.pt',
                 'bloc': 'lac:views/templates/file_result.pt'}

    def __init__(self, **kwargs):
        super(FileEntity, self).__init__(**kwargs)
        self.set_data(kwargs)


@implementer(IBaseReview)
class BaseReview(VisualisableElement, SearchableEntity):
    """Base Review class"""

    type_title = _('Base review')
    thumbnail = CompositeUniqueProperty('thumbnail')
    picture = CompositeUniqueProperty('picture')
    author = SharedUniqueProperty('author', 'contents')
    artists = SharedMultipleProperty('artists', 'creations')

    def __init__(self, **kwargs):
        self._presentation_text = None
        super(BaseReview, self).__init__(**kwargs)
        self.set_data(kwargs)

    def _init_presentation_text(self):
        self._presentation_text = html_article_to_text(
            getattr(self, 'article', ''))

    def __setattr__(self, name, value):
        super(BaseReview, self).__setattr__(name, value)
        if name == 'article':
            self._init_presentation_text()

    @property
    def relevant_data(self):
        result = super(BaseReview, self).relevant_data
        result.extend([', '.join([a.title for a in self.artists])])
        return result

    @property
    def artists_ids(self):
        return [str(get_oid(a)) for a in self.artists]

    def presentation_text(self, nb_characters=400):
        text = getattr(self, '_presentation_text', None)
        if text is None:
            self._init_presentation_text()
            text = getattr(self, '_presentation_text', '')

        return text[:nb_characters]+'...'

    def get_visibility_filter(self):
        result = super(BaseReview, self).get_visibility_filter()
        authors = [self.author] if self.author else []
        result.update({
            'contribution_filter': {'authors': authors}})
        return result


class AdvertisingSchema(VisualisableElementSchema, SearchableEntitySchema):
    """Schema for advertising"""

    visibility_dates = colander.SchemaNode(
        colander.String(),
        validator=dates_validator,
        widget=DateIcalWidget(),
        title=_('Dates'),
        )

    request_quotation = colander.SchemaNode(
        colander.Boolean(),
        widget=deform.widget.CheckboxWidget(),
        label=_('Request for quotation'),
        title='',
        missing=False
        )


@implementer(IAdvertising)
class Advertising(VisualisableElement, SearchableEntity):
    """Advertising class"""

    picture = CompositeUniqueProperty('picture')
    author = SharedUniqueProperty('author', 'contents')
    internal_type = True

    def __init__(self, **kwargs):
        super(Advertising, self).__init__(**kwargs)
        self.access_control = PersistentList([self.source_site])
