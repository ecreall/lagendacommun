# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Vincent Fretin

from hypatia.query import (
    BoolOp, NotInRange, InRange, Lt, Le, Gt, Ge, Any, Eq, NotAny, Or, And)
import hypatia.query
from hypatia._compat import xrange


class NoOpAny(Any):
    def _apply(self, names):
        return self.index.family.IF.Set()

    def negate(self):
        return NoOpNotAny(self.index, self._value)


class NoOpNotAny(NotAny):
    def _apply(self, names):
        return self.index.docids()

    def negate(self):
        return NoOpAny(self.index, self._value)


def _optimize_or(self):
    new_me = self._optimize_eq()
    if new_me is not None:
        return new_me

    new_me = self._optimize_not_eq()
    if new_me is not None:
        return new_me

    queries = [query._optimize() for query in self.queries]

    # There might be a combination of Gt/Ge and Lt/Le operators for the
    # same index that could be used to compose a NotInRange.
    uppers = {}
    lowers = {}
    queries_by_index = {}

    def process_range(i_lower, query_lower, i_upper, query_upper):
        queries[i_lower] = NotInRange.fromGTLT(
            query_lower.negate(), query_upper.negate())
        queries[i_upper] = None

    def process_any(i_first, query_first, i_second, query_second):
        values = set(query_first._value).union(query_second._value)
        new_query = Any(query_first.index, list(values))
        queries_by_index[new_query.index] = (i_first, new_query)
        queries[i_first] = new_query
        queries[i_second] = None

    for i in xrange(len(queries)):
        query = queries[i]
        if type(query) in (Lt, Le):
            match = uppers.get(query.index)
            if match is not None:
                i_upper, query_upper = match
                process_range(i, query, i_upper, query_upper)
            else:
                lowers[query.index] = (i, query)

        elif type(query) in (Gt, Ge):
            match = lowers.get(query.index)
            if match is not None:
                i_lower, query_lower = match
                process_range(i_lower, query_lower, i, query)
            else:
                uppers[query.index] = (i, query)

        elif type(query) == Any:
            match = queries_by_index.get(query.index)
            if match is not None:
                i_first, query_first = match
                process_any(i_first, query_first, i, query)
            else:
                queries_by_index[query.index] = (i, query)

        # TODO: NotAny, All, NotAll

    queries = [x for x in queries if x]
    if len(queries) == 1:
        return queries[0]

    # Factorize common parts
    # Example:
    # Or(And(Any1, Any2), And(Any1, Any3, Any4))
    # becomes:
    # And(Any1, Or(Any2, And(Any3, Any4)))
    ands = [q for q in queries if type(q) == And]
    # we can only factorize if all queries are And
    if len(ands) != len(queries):
        return self.__class__(*queries)

    factorized_queries = []
    for q in ands[0].queries:
        moveup = True
        # move up (factorize) q if q is in all And queries
        for and_query in ands[1:]:
            if q not in and_query.queries:
                moveup = False

        if moveup:
            # add q to the factorized queries
            factorized_queries.append(q)
            # and remove it from all And
            for idx, and_query in enumerate(ands):
                new_queries = list(and_query.queries)
                new_queries.remove(q)
                if len(new_queries) == 1:
                    ands[idx] = new_queries[0]
                else:
                    ands[idx] = And(*new_queries)

    all_queries = factorized_queries + [Or(*ands)]
    return And(*all_queries)


def _optimize_and(self):
    new_me = self._optimize_eq()
    if new_me is not None:
        return new_me

    new_me = self._optimize_not_eq()
    if new_me is not None:
        return new_me

    queries = [query._optimize() for query in self.queries]

    # There might be a combination of Gt/Ge and Lt/Le operators for the
    # same index that could be used to compose an InRange.
    uppers = {}
    lowers = {}
    queries_by_index = {}

    def process_range(i_lower, query_lower, i_upper, query_upper):
        queries[i_lower] = InRange.fromGTLT(query_lower, query_upper)
        queries[i_upper] = None

    def process_any(i_first, query_first, i_second, query_second):
        """Return True if merge of the two is empty.
        """
        # not any(['archived']) x any(['published'])
        # => any(['published'].difference(['archived']))
        if type(query_first) == type(query_second) == Any:
            values = set(query_first._value).intersection(query_second._value)
            new_query = Any(query_first.index, list(values))
        elif type(query_first) == type(query_second) == NotAny:
            values = set(query_first._value).union(query_second._value)
            new_query = NotAny(query_first.index, list(values))
        elif type(query_first) == NotAny:  # NotAny with Any
            values = set(query_second._value).difference(query_first._value)
            new_query = Any(query_first.index, list(values))
        else:  # Any with NotAny
            values = set(query_first._value).difference(query_second._value)
            new_query = Any(query_first.index, list(values))
        queries_by_index[new_query.index] = (i_first, new_query)
        queries[i_first] = new_query
        queries[i_second] = None
        return not values

    # flatten the tree
    arguments = []
    for query in queries:
        # If argument is of the same type, can promote its arguments up
        # to here.
        if type(query) == type(self):
            arguments.extend(query.queries)
        else:
            arguments.append(query)

    queries = arguments

    # merge Any/NotAny and Gt/Ge/Lt/Le
    for i in xrange(len(queries)):
        query = queries[i]
        if type(query) in (Gt, Ge):
            match = uppers.get(query.index)
            if match is not None:
                i_upper, query_upper = match
                process_range(i, query, i_upper, query_upper)
            else:
                lowers[query.index] = (i, query)

        elif type(query) in (Lt, Le):
            match = lowers.get(query.index)
            if match is not None:
                i_lower, query_lower = match
                process_range(i_lower, query_lower, i, query)
            else:
                uppers[query.index] = (i, query)

        elif type(query) in (Any, NotAny):
            match = queries_by_index.get(query.index)
            if match is not None:
                i_first, query_first = match
                empty = process_any(i_first, query_first, i, query)
                if empty:
                    return NoOpAny(query.index, [])
            else:
                queries_by_index[query.index] = (i, query)

        # TODO: All, NotAll

    queries = [x for x in queries if x]
    if len(queries) == 1:
        return queries[0]

    return self.__class__(*queries)


hypatia.query.Or._optimize = _optimize_or
hypatia.query.And._optimize = _optimize_and

"""
Without site query:

(Pdb) query.print_tree()
And
  <substanced.catalog.indexes.KeywordIndex object 'object_provides' at 0x7fc2d97d29e8> in any(['lac.content.interface.ICulturalEvent', 'lac.content.interface.IGame', 'lac.content.interface.IWebAdvertising', 'lac.content.interface.IFilmSchedule', 'lac.content.interface.IReview', 'lac.content.interface.IBrief', 'lac.content.interface.IOrganization', 'lac.content.interface.IArtistInformationSheet', 'lac.content.interface.IVenue', 'lac.content.interface.IFilmSynopses', 'lac.content.interface.IPerson', 'lac.content.interface.IGroup', 'lac.content.interface.ICinemaReview', 'lac.content.interface.IPeriodicAdvertising', 'lac.content.interface.IInterview'])
  <substanced.catalog.indexes.KeywordIndex object 'object_states' at 0x7fc2d97d2a58> not in any(['archived'])
  <substanced.catalog.indexes.KeywordIndex object 'object_provides' at 0x7fc2d97d29e8> in any(['lac.content.interface.IReview', 'lac.content.interface.IInterview'])
  <substanced.catalog.indexes.KeywordIndex object 'object_keywords' at 0x7fc2d975c7b8> in any(['rubrique/conférence'])
  <substanced.catalog.indexes.KeywordIndex object 'object_states' at 0x7fc2d97d2a58> in any(['published'])
  release_date >= datetime.datetime(2016, 3, 17, 19, 44, 49, 64722, tzinfo=<UTC>)
  <substanced.catalog.indexes.KeywordIndex object 'object_provides' at 0x7fc2d97d29e8> in any(['lac.content.interface.IInterview', 'lac.content.interface.ICinemaReview', 'lac.content.interface.IReview', 'lac.content.interface.IBrief'])
  <substanced.catalog.indexes.KeywordIndex object 'object_states' at 0x7fc2d97d2a58> in any(['published'])
  <substanced.catalog.indexes.KeywordIndex object 'access_keys' at 0x7fc2d975c358> in any(['anonymous', 'always'])
  datetime.datetime(2016, 4, 1, 0, 0, tzinfo=<UTC>) <= publication_start_date <= datetime.datetime(2016, 4, 1, 23, 59, 59, tzinfo=<UTC>)
(Pdb) query._optimize().print_tree()
And
  <substanced.catalog.indexes.KeywordIndex object 'object_provides' at 0x7fc2d97d29e8> in any(['lac.content.interface.IInterview', 'lac.content.interface.IReview'])
  <substanced.catalog.indexes.KeywordIndex object 'object_states' at 0x7fc2d97d2a58> in any(['published'])
  <substanced.catalog.indexes.KeywordIndex object 'object_keywords' at 0x7fc2d975c7b8> in any(['rubrique/conférence'])
  release_date >= datetime.datetime(2016, 3, 17, 19, 44, 49, 64722, tzinfo=<UTC>)
  <substanced.catalog.indexes.KeywordIndex object 'access_keys' at 0x7fc2d975c358> in any(['anonymous', 'always'])
  datetime.datetime(2016, 4, 1, 0, 0, tzinfo=<UTC>) <= publication_start_date <= datetime.datetime(2016, 4, 1, 23, 59, 59, tzinfo=<UTC>)


(Pdb) query.print_tree()
And
  <substanced.catalog.indexes.KeywordIndex object 'object_provides' at 0x7fbc17012748> in any(['lac.content.interface.ICulturalEvent'])
  <substanced.catalog.indexes.KeywordIndex object 'object_keywords' at 0x7fbc16fb6128> in any(['rubrique/conférence'])
  <substanced.catalog.indexes.KeywordIndex object 'object_states' at 0x7fbc170127b8> in any(['published'])
  <substanced.catalog.indexes.KeywordIndex object 'object_access_control' at 0x7fbc16fabeb8> in any(['all', '7518384164125415137'])
  datetime.datetime(2016, 4, 1, 0, 0, tzinfo=<UTC>) <= start_date <= datetime.datetime(2016, 4, 16, 0, 0, tzinfo=<UTC>)
  release_date >= datetime.datetime(2016, 3, 16, 20, 22, 29, 364427, tzinfo=<UTC>)
  <substanced.catalog.indexes.KeywordIndex object 'object_provides' at 0x7fbc17012748> in any(['lac.content.interface.ICinemaReview', 'lac.content.interface.IReview', 'lac.content.interface.IBrief', 'lac.content.interface.IInterview'])
  <substanced.catalog.indexes.KeywordIndex object 'object_states' at 0x7fbc170127b8> in any(['published'])
  <substanced.catalog.indexes.KeywordIndex object 'object_access_control' at 0x7fbc16fabeb8> in any(['all', '7518384164125415137'])
(Pdb) query._optimize().print_tree()
<substanced.catalog.indexes.KeywordIndex object 'object_provides' at 0x7fa806292438> in any([])


With site_query
(Pdb) query.print_tree()
And
  Or
    And
      <substanced.catalog.indexes.KeywordIndex object 'object_provides' at 0x7f55f1850748> in any(['lac.content.interface.IVenue', 'lac.content.interface.IWebAdvertising', 'lac.content.interface.IGame', 'lac.content.interface.IFilmSchedule', 'lac.content.interface.ICinemaReview', 'lac.content.interface.IPeriodicAdvertising', 'lac.content.interface.IPerson', 'lac.content.interface.IInterview', 'lac.content.interface.ICulturalEvent', 'lac.content.interface.IArtistInformationSheet', 'lac.content.interface.IGroup', 'lac.content.interface.IOrganization', 'lac.content.interface.IReview', 'lac.content.interface.IFilmSynopses', 'lac.content.interface.IBrief'])
      <substanced.catalog.indexes.KeywordIndex object 'object_states' at 0x7f55f18507b8> not in any(['archived'])
      '62??? OR 60??? OR 02??? OR 59??? OR 80??? OR anywhere' in <substanced.catalog.indexes.TextIndex object 'object_zipcode_txt' at 0x7f55f17f63c8>
      <substanced.catalog.indexes.KeywordIndex object 'object_access_control' at 0x7f55f17e8eb8> in any(['all', '7518384164125415137'])
    And
      <substanced.catalog.indexes.KeywordIndex object 'object_provides' at 0x7f55f1850748> in any(['lac.content.interface.IVenue', 'lac.content.interface.IWebAdvertising', 'lac.content.interface.IGame', 'lac.content.interface.IFilmSchedule', 'lac.content.interface.ICinemaReview', 'lac.content.interface.IPeriodicAdvertising', 'lac.content.interface.IPerson', 'lac.content.interface.IInterview', 'lac.content.interface.ICulturalEvent', 'lac.content.interface.IArtistInformationSheet', 'lac.content.interface.IGroup', 'lac.content.interface.IOrganization', 'lac.content.interface.IReview', 'lac.content.interface.IFilmSynopses', 'lac.content.interface.IBrief'])
      <substanced.catalog.indexes.KeywordIndex object 'object_states' at 0x7f55f18507b8> not in any(['archived'])
      <substanced.catalog.indexes.KeywordIndex object 'object_country' at 0x7f55f17f6048> in any(['belgique', 'anywhere'])
      <substanced.catalog.indexes.KeywordIndex object 'object_access_control' at 0x7f55f17e8eb8> in any(['all', '7518384164125415137'])
  <substanced.catalog.indexes.KeywordIndex object 'object_provides' at 0x7f55f1850748> in any(['lac.content.interface.IInterview', 'lac.content.interface.IReview'])
  <substanced.catalog.indexes.KeywordIndex object 'object_keywords' at 0x7f55f17f6128> in any(['rubrique/conférence'])
  <substanced.catalog.indexes.KeywordIndex object 'object_states' at 0x7f55f18507b8> in any(['published'])
  <substanced.catalog.indexes.KeywordIndex object 'object_access_control' at 0x7f55f17e8eb8> in any(['all', '7518384164125415137'])
  release_date >= datetime.datetime(2016, 3, 16, 20, 27, 37, 623068, tzinfo=<UTC>)
  <substanced.catalog.indexes.KeywordIndex object 'object_provides' at 0x7f55f1850748> in any(['lac.content.interface.IInterview', 'lac.content.interface.ICinemaReview', 'lac.content.interface.IReview', 'lac.content.interface.IBrief'])
  <substanced.catalog.indexes.KeywordIndex object 'object_states' at 0x7f55f18507b8> in any(['published'])
  <substanced.catalog.indexes.KeywordIndex object 'object_access_control' at 0x7f55f17e8eb8> in any(['all', '7518384164125415137'])
  <substanced.catalog.indexes.KeywordIndex object 'access_keys' at 0x7f55f17e8c88> in any(['admin_7422658066368290765', 'always'])
(Pdb) query._optimize().print_tree()
And
  <substanced.catalog.indexes.KeywordIndex object 'object_provides' at 0x7f55f1850748> in any(['lac.content.interface.IInterview', 'lac.content.interface.IReview'])
  <substanced.catalog.indexes.KeywordIndex object 'object_states' at 0x7f55f18507b8> in any(['published'])
  <substanced.catalog.indexes.KeywordIndex object 'object_access_control' at 0x7f55f17e8eb8> in any(['all', '7518384164125415137'])
  Or
    '62??? OR 60??? OR 02??? OR 59??? OR 80??? OR anywhere' in <substanced.catalog.indexes.TextIndex object 'object_zipcode_txt' at 0x7f9dba9f9048>
    <substanced.catalog.indexes.KeywordIndex object 'object_country' at 0x7f9dba9f0c88> in any(['belgique', 'anywhere'])
  <substanced.catalog.indexes.KeywordIndex object 'object_keywords' at 0x7f55f17f6128> in any(['rubrique/conférence'])
  release_date >= datetime.datetime(2016, 3, 16, 20, 27, 37, 623068, tzinfo=<UTC>)
  <substanced.catalog.indexes.KeywordIndex object 'access_keys' at 0x7f55f17e8c88> in any(['admin_7422658066368290765', 'always'])

"""
