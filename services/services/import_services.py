
import urllib
import json
import os
from xml import sax

from .transformations import DigitickToCreationculturelle
from .config import digitick_source


class Element(object):

    def __init__(self, node=None):
        self._node = node

    def setData(self, key, value):
        self.__dict__[key] = value

    def setObject(self, key, object):
        if key in self.__dict__ and not \
           isinstance(self.__dict__[key], (list, tuple)):
            prev_object = self.__dict__[key]
            self.__dict__[key] = []
            self.__dict__[key].append(prev_object)
            self.__dict__[key].append(object)
        elif key in self.__dict__:
            self.__dict__[key].append(object)
        else:
            self.__dict__[key] = object

    def jsonable(self):
        return self._traverse(self.__dict__)

    def _traverse(self, obj):
        if isinstance(obj, dict):
            for k in obj.keys():
                obj[k] = self._traverse(obj[k])
            return obj
        elif isinstance(obj, (list, tuple)):
            return [self._traverse(v) for v in obj]
        elif isinstance(obj, Element):
            data = [(key, self._traverse(value))
                    for key, value in obj.__dict__.items()
                    if not callable(value) and not key.startswith('_')]

            if not data:
                return None

            return data
        else:
            return obj


class DictBuilder(sax.ContentHandler):

    def __init__(self, nodes):
        sax.ContentHandler.__init__(self)
        self.obj = []
        self.nodes = nodes
        self.fetch = False
        self.__buffer = ''

    def startElementNS(self, name, qname, attrs):
        (ns, localname) = name
        if localname in self.nodes:
            self.fetch = True
            item = Element(localname)
            self.rootobject = item
            self.obj.append(item)
        elif self.fetch:
            self.__buffer = ''
            item = Element()
            self.obj[-1].setObject(localname, item)
            self.obj.append(item)

    def characters(self, contents):
        if self.fetch:
            self.__buffer += contents.strip()

    def endElementNS(self, name, qname):
        (ns, localname) = name
        if localname in self.nodes:
            self.fetch = False
            data = self.rootobject.jsonable()
        elif self.fetch:
            if self.__buffer != '':
                self.obj[-2].setData(localname, self.__buffer)
            del self.obj[-1]
            self.__buffer = ''

    def jsonable(self):
        result = []
        for element in self.obj:
            element_type = element._node
            element_dict = element.__dict__.copy()
            element_dict['node_type'] = element_type
            result.append(element_dict)

        return result


class DataLoader(object):

    def load(self, source, content_type):
        """Return Json dic. 'source' is a source file source,
           'content_type' is the content type to load"""
        pass


class XMLLoader(DataLoader):

    def load(self, source, content_types):
        """Return Json dic. 'source' is a source XML file source,
           'content_type' is the content type to load"""
        parser = sax.make_parser()
        parser.setContentHandler(DictBuilder(content_types))
        parser.setFeature(sax.handler.feature_namespaces, 1)
        inpsrc = urllib.request.urlopen(source)
        parser.parse(inpsrc)
        return parser.getContentHandler().jsonable()


class Service(object):

    loader = None

    def source(self):
        """Return the url of the file source"""
        pass

    def import_entities(self, content_types):
        """Import and transform entities from sourse.
           See  source operation"""
        return []


class DigitickService(Service):

    loader = XMLLoader()
    transformation = DigitickToCreationculturelle()
    content_types_mapping = {'cultural_event': 'evenement'}

    def source(self):
        return digitick_source

    def import_entities(self, content_types):
        #recuperate types accepted by digitick
        digitick_types = [self.content_types_mapping.get(content_type) \
                         for content_type in content_types \
                         if self.content_types_mapping.get(content_type, None)]
        if digitick_types:
            #recuperate all of entries provided by digitick
            result = self.loader.load(self.source(), digitick_types)
            try:
                #Transform recuperated entities.
                #See DigitickToCreationculturelle transformation (.transformations.py)
                transformed_result = [self.transformation.do_transformation(r)\
                                      for r in result]
                #Return transformed entities
                return [res for res in transformed_result if res]
            except Exception:
                return []

        return []


SERVICES = {'digitick': DigitickService()}


def export_entities(content_types, target):
    """Recuperate and save all entities from all services.
       'content_types' are types to import from services.
       'target' is an url where imported entities well be saved"""

    all_result = []
    #Recuperate all entities from all services
    for service in SERVICES.values():
        all_result.extend(service.import_entities(content_types))

    target_path = urllib.parse.urlparse(target)
    final_path = os.path.abspath(
                  os.path.join(
                     target_path.netloc, target_path.path))
    out = open(final_path, 'w')
    #Save imported entities
    json.dump(all_result, out)
    out.close()
