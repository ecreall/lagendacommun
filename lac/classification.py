# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi, Sophie Jazwiecki, Michael Launay
import time
import re
import io
import zipfile
from collections import defaultdict
from lxml import etree

import venusian
import datetime
import pytz
from pyramid import renderers
from pyramid.threadlocal import get_current_registry

from substanced.util import get_oid

from dace.objectofcollaboration.principal.util import get_current
from dace.util import find_catalog
from dace.processinstance.core import ExecutionError

from lac.content.site_configuration import (
    DEFAULT_DAYS_VISIBILITY)
from lac import _, CLASSIFICATIONS
from lac.content.interface import ISmartFolder
from lac.utilities.smart_folder_utility import get_folder_content
from lac.utilities.ical_date_utility import (
    occurences_start, getDatesFromString)
from lac.views.filter import find_entities
from lac.adapters.searchable_object_adapter import (
    ISearchableObject)
from lac.utilities.utils import get_site_folder
from lac.utilities.ical_date_utility import getMiseAJourSeance


ODT_NAME_SPACES = {
    'office': "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    'style': "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    'text': "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    'table': "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    'draw': "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    'fo': "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    'xlink': "http://www.w3.org/1999/xlink",
    'dc': "http://purl.org/dc/elements/1.1/",
    'meta': "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
    'number': "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0",
    'svg': "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
    'chart': "urn:oasis:names:tc:opendocument:xmlns:chart:1.0",
    'dr3d': "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0",
    'math': "http://www.w3.org/1998/Math/MathML",
    'form': "urn:oasis:names:tc:opendocument:xmlns:form:1.0",
    'script': "urn:oasis:names:tc:opendocument:xmlns:script:1.0",
    'ooo': "http://openoffice.org/2004/office",
    'ooow': "http://openoffice.org/2004/writer",
    'oooc': "http://openoffice.org/2004/calc",
    'dom': "http://www.w3.org/2001/xml-events",
    'xforms': "http://www.w3.org/2002/xforms",
    'xsd': "http://www.w3.org/2001/XMLSchema",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance"
}

REG_EUROS = re.compile("([1-9]+[0-9]|[2-9])([.,][0-9]*)?")
REG_URL = re.compile("(((http[:][/][/])(www)?|www)[0-9a-zA-Z.]*)|([A-Z]([.][A-Z])+)")
capitalize_1st_char = lambda sentences: sentences and sentences[0].upper() + sentences[1:]
lower_1st_char = lambda sentences: sentences and sentences[0].lower() + sentences[1:]
capitalize_sentences_with_dot = lambda sentences: sentences.find(".") >= 0 and ". ".join([capitalize_1st_char(x.strip()) for x in sentences.split(".")]) or sentences
capitalize_questions = lambda sentences: sentences.find("?") >= 0 and " ? ".join([capitalize_1st_char(y.strip()) for y in sentences.split("?")]) or sentences
capitalize_exclamations = lambda sentences: sentences.find("!") >= 0 and " ! ".join([capitalize_1st_char(z.strip()) for z in sentences.split("!")]) or sentences
capitalize_all_sentences_with_semicolon = lambda sentences: sentences.find(";") >= 0 and " ; ".join([capitalize_1st_char(z.strip()) for z in sentences.split(";")]) or sentences
capitalize_sentences = lambda sentences: capitalize_all_sentences_with_semicolon(
      capitalize_exclamations(
        capitalize_questions(
          capitalize_sentences_with_dot(sentences))))


def french_normalize(text):
    """ Capitalize first caracter of sentences and add the dot at the end of sentences by taking care of urls.
        Add the french indentation after mark (dot, question, coma, semicolon).
    """
    text = text.replace("\n", "")
    text = text.strip()
    if not text:
        return ""
    ECHAP_POINT = "{AN_ECHAP_POINT}"
    substitutes = [(x.start(), x.end(), text[x.start(): x.end()].\
                   replace(".", ECHAP_POINT))
                   for x in re.finditer(REG_URL, text)]
    position = 0
    new_text = ""
    for substitute in substitutes:
        new_text += text[position:substitute[0]] + substitute[2]
        position = substitute[1]
    new_text += text[position:]
    new_text = capitalize_sentences(new_text)
    new_text = new_text.replace(ECHAP_POINT, ".")
    text = '\u2026'.join(new_text.split(". . .")).strip()
    if not text:
        text = ". . ."

    if not text[-1] in [".", "?", "!", '\u2026']:
        text += "."

    return text


def date_normalize(date_str, context, site, filter_parameters,
                   force_complete_date=False,
                   update_schedule=getMiseAJourSeance,
                   string_normalize=french_normalize):
    """ Compress the event extracted date, for example if the event has only
        one date AND the classment is by date, return only the hour of the event
        because the day is provided for the paragraph.
        Remove dates wich are not in the search lapse of time
    """
    temporal_filter = filter_parameters.get('temporal_filter', {})
    default_date = getattr(site, 'publication_date', datetime.datetime.now())
    start_date = temporal_filter.get(
        'start_end_dates', {}).get('start_date', default_date)
    start_date = start_date if start_date else default_date
    end_date = temporal_filter.get(
        'start_end_dates', {}).get('end_date', None)
    return string_normalize(
        update_schedule(date_str, start_date, end_date, context=context)[0])


DATE_EXPRESSION = re.compile("20[0-9][0-9][0-1][0-9][0-3][0-9]T")


def has_only_one_date(date, content):
    """ Check if the object has only one schedule
    """
    if len(content.schedules) > 1: #@TODO do not count filter pass dates so this test is not good
        return False
    dates = content.schedules[0].dates_recurrence
    if len(DATE_EXPRESSION.findall(dates)) > 1:
        return False
    return True


class classification(object):
    """ Decorator for classifications"""

    def __call__(self, wrapped):
        def callback(scanner, name, ob):
            if ob.classification_id not in CLASSIFICATIONS:
                CLASSIFICATIONS[ob.classification_id] = ob

        venusian.attach(wrapped, callback)
        return wrapped


class Classification(object):
    """ Abstract classification"""
    templates = NotImplemented
    start_value = None
    end_value = None
    omit = []
    select = []
    classification_id = "classification"
    title = _("Classification")
    description = ""
    default_value = None

    def __init__(self, subclassification=None):
        self.subclassification = subclassification
        self.__parent__ = None
        if subclassification:
            subclassification.__parent__ = self

    def root(self):
        if self.__parent__ is None:
            return self

        return self.__parent__.root()

    def all_classifications(self):
        result = [self]
        if self.subclassification:
            result.extend(self.subclassification.all_classifications())
        return result

    def _is_equal(self, value1, value2):
        return value1 == value2

    def _is_greater(self, value1, value2):
        return value1 > value2

    def _is_lower(self, value1, value2):
        return value1 < value2

    def _is_in(self, value, values):
        return value in values

    def _getattribute(self, value, **args):
        pass

    def get_query(self, **args):
        pass

    def sort(self, values):
        return sorted(values, key=lambda e: e[0])

    def getattributes(self, values, **args):
        attributes = [self._getattribute(v, **args) for v in values]
        attributes = [item for sublist in attributes for item in sublist]
        result = {self: attributes}
        if self.subclassification:
            result.update(self.subclassification.getattributes(values, **args))

        return result

    def classification(self, values, attributes, **args):
        items = [a for a in attributes[self] if a[0] in values]
        items_dict = {}
        items_dict = defaultdict(list)
        for value, classifier in items:
            items_dict[classifier].append(value)

        result = [(key, (value, len(value)))
                  for key, value in items_dict.items()]

        if self.subclassification:
            result = [(key, (self.subclassification.classification(
                value[0], attributes, **args), value[1]))
                for key, value in result]

        if self.omit:
            result = [value for value in result
                      if not self._is_in(value[1][0], self.omit)]

        if self.select:
            result = [value for value in result
                      if self._is_in(value[1][0], self.select)]

        return result

    def _render(self, values, bodies, request, folder, **args):
        template_type = args.get('template_type', 'default')
        filter_body = args.pop('filter_body', None)
        inverse_substitutions = args.get('inverse_substitutions', {})
        if self.subclassification:
            result = [(key, ([self.subclassification._render(
                items, bodies,
                request, folder,
                **args)], len_items))
                for key, (items, len_items) in values if items]
        else:
            def _to_set(objects):
                substitutions = []
                for obj in objects:
                    sub = inverse_substitutions.get(obj, None)
                    if sub not in substitutions:
                        substitutions.append(sub)
                        yield obj

            result = [(key, ([bodies[obj]
                              for obj in _to_set(items)], len_items))
                      for key, (items, len_items) in values]

        user = get_current()
        values = {'items': self.sort(result),
                  'folder': folder,
                  'current_user': user,
                  'current_date': datetime.datetime.now(),
                  'filter_parameters': args.get('filters', []),
                  'classification': self}
        if filter_body:
            values.update({'filter_body': filter_body})

        template = self.templates.get(template_type, 'default')
        body = renderers.render(template,
                                values, request)
        return body

    def render(self, values, request, folder, **args):
        template_type = args.get('template_type', 'default')
        user = get_current()
        bodies = {}
        values = list(values)
        substitutions = []
        inverse_substitutions = {}
        for value in values:
            object_values = {'object': value,
                             'current_user': user,
                             'state': None}
            body = renderers.render(value.templates[template_type],
                                    object_values, request)
            value_substitutions = value.substitutions
            inverse_substitutions.update({substitution: value for substitution
                                          in value_substitutions})
            bodies.update({substitution: body for substitution
                           in value_substitutions})
            substitutions.extend(value_substitutions)

        validated = args.get('validated', {})
        if isinstance(validated, list) and validated:
            validated = validated[0]

        attributes = self.getattributes(
            substitutions,
            inverse_substitutions=inverse_substitutions,
            **validated)
        items_classified = self.classification(
            substitutions, attributes, **validated)
        return self._render(items_classified, bodies,
                            request, folder,
                            inverse_substitutions=inverse_substitutions,
                            **args)

    def extract(self, values, request, folder, **args):
        user = get_current()
        site = get_site_folder(True)
        bodies = {}
        has_date_classification = any(isinstance(c, DateClassification)
                                      for c in self.all_classifications())
        values = list(values)
        filter_parameters = args.get('filters', [])
        filter_parameters = filter_parameters[0] if filter_parameters else {}
        substitutions = []
        inverse_substitutions = {}
        for value in values:
            object_values = {'object': value,
                             'current_user': user,
                             'state': None,
                             'has_date_classification': has_date_classification,
                             'has_only_one_date': has_only_one_date,
                             'date_normalize': date_normalize,
                             'filter_parameters': filter_parameters,
                             'text_normalize': french_normalize,
                             'site': site} #@TODO generalyse to apply the specific language normalization function not always french
            body = renderers.render(value.templates.get('extraction', None),
                                    object_values, request)
            value_substitutions = value.substitutions
            inverse_substitutions.update({substitution: value for substitution
                                          in value_substitutions})
            bodies.update({substitution: body for substitution
                           in value_substitutions})
            substitutions.extend(value_substitutions)

        validated = args.get('validated', filter_parameters)
        if isinstance(validated, list) and validated:
            validated = validated[0]

        attributes = self.getattributes(
            substitutions, extraction_processing=True,
            inverse_substitutions=inverse_substitutions, **validated)
        items_classified = self.classification(substitutions, attributes, **validated)
        args.update({'extraction': True})
        odt_content = self._render(items_classified, bodies,
                            request, folder,
                            inverse_substitutions=inverse_substitutions,
                            **args).replace('\\n', '').\
                                                    replace('\\r', ' ').\
                                                    replace("\\'", "'").\
                                                    replace("\x1f", "")
        odt_content.encode("utf-8", 'replace')
        user_name = user.name
        extraction_template_file = site.extraction_template
        s_out = None
        if not extraction_template_file:
            raise ExecutionError(msg=_("You must configure the extraction"
                                       " ODT Pattern File"))

        with zipfile.ZipFile(extraction_template_file.fp) as template_zip:
            odt_meta = etree.parse(
                io.BytesIO(template_zip.read('meta.xml')),
                etree.XMLParser())
            # Update metadatas
            tag_generator = odt_meta.xpath("//meta:generator",
                                namespaces=ODT_NAME_SPACES)
            tag_generator[0].text = \
                "ecreall.com/CreationCulturelle/Extraction.0.2".encode("utf-8")
            tag_creator = odt_meta.xpath("//dc:creator",
                namespaces=ODT_NAME_SPACES)
            tag_creator[0].text = user_name.encode("utf-8")
            tag_date = odt_meta.xpath("//dc:date", namespaces=ODT_NAME_SPACES)
            tag_date[0].text = time.strftime("%Y-%m-%dT%H:%M:%S",
                time.localtime()).encode("utf-8")
            tag_editingCycle = odt_meta.xpath("//meta:editing-cycles",
                namespaces=ODT_NAME_SPACES)
            tag_editingCycle[0].text = '1'

            # Generate new odt file from template with the meta file updated
            # and the extract content
            s_out = io.BytesIO()
            with zipfile.ZipFile(s_out, 'w') as zip_out:
                for a_file in template_zip.infolist():
                    if a_file.filename == 'content.xml':
                        zip_out.writestr(a_file, odt_content)
                    elif a_file.filename == 'meta.xml':
                        zip_out.writestr(a_file, etree.tostring(
                            odt_meta,
                            encoding="UTF-8",
                            xml_declaration=True,
                            pretty_print=True))
                    else:
                        zip_out.writestr(
                            a_file,
                            template_zip.read(a_file.filename))
            s_out.seek(0)
        return s_out


@classification()
class CityClassification(Classification):
    default_value = 'None'
    classification_id = "city_classification"
    title = _("City classification")
    description = _("Classification by city")
    templates = {'default': 'lac:views/templates/classifications/city_classification.pt',
                 'extraction': 'lac:views/templates/classifications/extraction/city_classification.pt'}

    def _getattribute(self, value, **args):
        adapter = get_current_registry().queryAdapter(value, ISearchableObject)
        if adapter is None:
            return [(value, self.default_value)]

        cities = adapter.object_city()
        return [(value, c.title()) for c in cities]


@classification()
class DateClassification(Classification):

    default_value = '-1' #TODO to edit
    classification_id = "date_classification"
    title = _("Date classification")
    description = _("Classification by date")
    templates = {'default': 'lac:views/templates/classifications/date_classification.pt',
                 'extraction': 'lac:views/templates/classifications/extraction/date_classification.pt'}

    def _init_values(self, **args):
        #get validated data (Filter)
        start_end_dates = args.get('temporal_filter', {}).get('start_end_dates', {})
        if self.start_value is None:
            start_date = start_end_dates.get('start_date', None)
            self.start_value = ((start_date is not None) and start_date) or\
                datetime.datetime.now(tz=pytz.UTC)
            self.start_value = datetime.datetime.combine(
                self.start_value,
                datetime.time(0, 0, 0, tzinfo=pytz.UTC))

        if self.end_value is None:
            end_date = start_end_dates.get('end_date', None)
            if end_date:
                self.end_value = datetime.datetime.combine(
                    end_date,
                    datetime.time(23, 59, 59, tzinfo=pytz.UTC))
            elif 'ignore_end_date' not in args:
                site = get_site_folder(True)
                days_visibility = getattr(site, 'days_visibility',
                                          DEFAULT_DAYS_VISIBILITY)
                default_date = datetime.timedelta(days_visibility-1) + \
                    self.start_value
                self.end_value = default_date

    def _getattribute(self, value, **args):
        self._init_values(**args)
        dates = []
        if hasattr(value, 'dates_recurrence'):
            dates = occurences_start(value, 'dates',
                                     self.start_value, self.end_value,
                                     hours=0, minutes=0)
            if 'extraction_processing' in args:
                if dates:
                    return [(value, dates[0])]

                return []

            return [(value, d) for d in dates]

        return [(value, self.default_value)]

    def get_query(self, **args):
        self._init_values(**args)
        lac_catalog = find_catalog('lac')
        start = lac_catalog['start_date']
        return start.inrange(self.start_value, self.end_value)


@classification()
class SectionClassification(Classification):

    default_value = object() #TODO to edit
    classification_id = "section_classification"
    title = _("Section classification")
    description = _("Classification by section")
    templates = {'default': 'lac:views/templates/classifications/section_classification.pt',
                 'extraction': 'lac:views/templates/classifications/extraction/section_classification.pt'}

    def sort(self, values):
        site = get_site_folder(True)
        site_id = get_oid(site)
        return sorted(values,
                      key=lambda e: e[0].get_order(site_id) \
                                    if e[0] is not self.default_value else 1000)

    def _getattribute(self, value, folders_results, **args):
        inverse_substitutions = args.get('inverse_substitutions', {})
        oid = get_oid(inverse_substitutions.get(value, value))
        result = [(value, folder) for folder in folders_results
                  if oid in list(folders_results[folder])]
        if not result:
            result = [(value, self.default_value)]

        return result

    def _render(self, values, bodies, request, folder, **args):
        template_type = args.get('template_type', 'default')
        filter_body = args.pop('filter_body', None)
        inverse_substitutions = args.get('inverse_substitutions', {})
        if self.subclassification:
            result = {key: ([self.subclassification._render(
                items, bodies, request,
                (((self.default_value is key) and folder) or key),
                **args)], len_items)
                for key, (items, len_items) in values if items}
        else:
            def _to_set(objects):
                substitutions = []
                for obj in objects:
                    sub = inverse_substitutions.get(obj, None)
                    if sub not in substitutions:
                        substitutions.append(sub)
                        yield obj

            result = {key: ([bodies[obj] for obj in _to_set(items)], len_items)
                      for key, (items, len_items) in values}

        values = {'items': self.sort(list(result.items())),
                  'folder': folder,
                  'classification': self}
        if filter_body:
            values.update({'filter_body': filter_body})

        template = self.templates.get(template_type, 'default')
        body = renderers.render(template,
                                values, request)
        return body

    def getattributes(self, values, **args):
        inverse_substitutions = args.get('inverse_substitutions', {})
        user = get_current()
        folders = find_entities(
            interfaces=[ISmartFolder],
            metadata_filter={'states': ['published']},
            force_local_control=True)
        folders = [sf for sf in folders if not sf.parents]
        values_oids = [get_oid(inverse_substitutions.get(value, value))
                       for value in values]
        folders_results = {}
        for folder in folders:
            result_set = get_folder_content(folder, user, sort_on=None,
                intersect=values_oids, **args)
            folders_results[folder] = result_set.ids

        attributes = [self._getattribute(v, folders_results, **args)
                      for v in values]
        attributes = [item for sublist in attributes
                      for item in sublist]
        result = {self: attributes}
        if self.subclassification:
            result.update(self.subclassification.getattributes(values, **args))

        return result


@classification()
class VenueClassification(Classification):

    default_value = 'None'
    classification_id = "venue_classification"
    title = _("Venue classification")
    description = _("Classification by venue")
    templates = {'default': 'lac:views/templates/classifications/venue_classification.pt',
                 'extraction': 'lac:views/templates/classifications/extraction/venue_classification.pt'}

    def sort(self, values):
        return sorted(values, key=lambda e: e[0].title)

    def _getattribute(self, value, **args):
        adapter = get_current_registry().queryAdapter(value, ISearchableObject)
        if adapter is None:
            return [(value, self.default_value)]

        venues = adapter.object_venue()
        return [(value, c) for c in venues]


@classification()
class ReleaseDateClassification(Classification):

    default_value = '-1' #TODO to edit
    classification_id = "release_date_classification"
    title = _("Release date classification")
    description = _("Classification by release date")
    templates = {'default': 'lac:views/templates/classifications/date_classification.pt',
                 'extraction': 'lac:views/templates/classifications/extraction/date_classification.pt'}

    def _getattribute(self, value, **args):
        inverse_substitutions = args.get('inverse_substitutions', {})
        date = getattr(
            inverse_substitutions.get(value, value),
            'modified_at', None)
        if date:
            date = datetime.datetime.combine(
                date,
                datetime.time(0, 0, 0, tzinfo=pytz.UTC))
            return [(value, date)]

        return [(value, self.default_value)]


@classification()
class AlphabeticalClassification(Classification):

    default_value = '-1' #TODO to edit
    classification_id = "alphabetical_classification"
    title = _("Alphabetical classification")
    description = _("Alphabetical classification")
    templates = {'default': 'lac:views/templates/classifications/alphabetical_classification.pt',
                 'extraction': 'lac:views/templates/classifications/extraction/alphabetical_classification.pt'}

    def _getattribute(self, value, **args):
        inverse_substitutions = args.get('inverse_substitutions', {})
        return [(value, inverse_substitutions.get(value, value).title[0])]
