# Copyright (c) 2015 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi, Sophie Jazwiecki

import os
import time
from zope.interface import Interface, implementer

from elasticsearch.client import Elasticsearch
from arango import Arango

from dace.util import utility

from lac import log


ELASTICSEARCH_PORT = os.getenv('ELASTICSEARCH_PORT', 'localhost:9200')
es = Elasticsearch(ELASTICSEARCH_PORT)

ARANGO_HOST, ARANGO_PORT = os.getenv(
    'ARANGO_PORT', 'localhost:8529').split(':')
ARANGO_ROOT_PASSWORD = os.getenv('ARANGO_ROOT_PASSWORD', '')

arango_server = Arango(
    host=ARANGO_HOST, port=ARANGO_PORT,
    password=ARANGO_ROOT_PASSWORD)


class IResourceManager(Interface):

    def add_entry(self, key, value, mapping={}, id=None):
        pass

    def set_entry(self, key, value, id):
        pass

    def get_entry(self, id):
        pass

    def get_entries(self, key=None, query={"match_all": {}},
                    params={}, sort={}, fields=[]):
        pass

    def remove_entries(self, key=None, query={}):
        pass

    def remove_entry(self, id):
        pass


def normalize_value_types(value):
    if isinstance(value, dict):
        return {key: normalize_value_types(v)
                for key, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [normalize_value_types(v) for v in value]

    return value


def normalize_value(values):
    result = {}
    for key, value in values.items():
        if key.endswith('suggest'):
            result[key] = normalize_value_types(value)

        elif isinstance(value, dict):
            for key_value in value:
                new_key = key + "_" + key_value
                new_value = value[key_value]
                if isinstance(new_value, set):
                    new_value = list(new_value)

                result[new_key] = new_value
        else:
            if isinstance(value, set):
                value = list(value)

            result[key] = value

    return normalize_value_types(result)


@utility(name='elasticsearch_resource_manager')
@implementer(IResourceManager)
class ElasticSearchResourceManager(object):

    def create_index(self):
        try:
            try:
                exists = es.indices.exists('lac')
            except Exception:
                # wait elasticsearch start and check again
                time.sleep(5)
                exists = es.indices.exists('lac')

            if not exists:
                es.indices.create(
                    index='lac',
                    body={'settings': {
                            'number_of_replicas': 0,
                            'number_of_shards': 1,
                        }},
                    ignore=400)
                # RequestError: TransportError(400, u'IndexAlreadyExistsException[[lac] already exists]')
                return False
        except Exception as e:
            log.warning(e)

        return True

    def remove_index(self):
        try:
            es.indices.delete(index='lac', ignore=[400, 404])
        except Exception as e:
            # NotFoundError: TransportError(404, u'IndexMissingException[[lac] missing]')
            log.warning(e)

    @property
    def index(self):
        return es

    def add_entry(self, key, value, mapping={}, id=None):
        """Send entry to elasticsearch."""
        result = normalize_value(value)
        if not es.indices.exists_type('lac', key):
            es.indices.put_mapping(
                index='lac',
                doc_type=key,
                body={
                        key: {
                            'properties': mapping
                        }
                }
            )
        return es.index(index='lac', doc_type=key,
                        body=result, id=id,
                        refresh=True)

    def set_entry(self, key, value, id):
        result = normalize_value(value)
        return es.index(index='lac', doc_type=key,
                        body=result, id=id,
                        refresh=True)

    def get_entry(self, id):
        try:
            results = es.get(index='lac', id=id)
        except Exception as e:
            log.warning(e)
            return None

        if results:
            return results['_source']

        return None

    def get_entries(self, key=None, query={"match_all": {}},
                    params={}, sort={}, fields=[]):
        try:
            body = {'query': query,
                    'sort': sort
                    }
            if fields:
                body['fields'] = fields

            results = es.search(index='lac',
                                doc_type=key,
                                params=params,
                                body=body)
        except Exception as e:
            log.warning(e)
            return None, 0

        total = results['hits']['total']
        return results['hits']['hits'], total

    def remove_entries(self, key=None, query={}):
        pass

    def remove_entry(self, key, id):
        try:
            results = es.delete(index='lac',
                                doc_type=key,
                                id=id,
                                refresh=True)
        except Exception as e:
            log.warning(e)


default_resourcemanager = 'elasticsearch_resource_manager'


def arango_db__check():
    try:
        arango_server.create_database("lac")
    except Exception:
        pass

arango_db__check()


def create_collection(db, id_):
    try:
        db.create_collection(id_)
    except Exception:
        pass

    return db.col(id_)
