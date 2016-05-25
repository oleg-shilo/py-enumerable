__author__ = 'ViraLogic Software'
# https://github.com/viralogic/py-enumerable

# Implementation changes:
#   + removed __init__.py to reflect py3 changes around importing and
#   __init__.py
#     (see '(removed)__init__.py' for details).  Though this work around may
#     need to be rolled back
#     when packaging for pip.
#   + fixed intercept
#   + used built-in map
#   + fixed all default params that accept rich objects (e.g. [], lambdas) ref:http://docs.python-guide.org/en/latest/writing/gotchas/
#   + added implicit Enumerable wrapping
#   + work around for dicts being no longer sortable: "unorderable types:
#   dict() < dict()"
#   + fixes 'last' (removed pre-ordering)
#   + fixes in unit testing infrastructure
#   + fixed 'def intersect' error: "sublist parameters are not supported in
#   3.x"
#   + implemented 'reverse'
#   + implemented 'foreach'
#
# Unit tests
#   + updated u.tests to reflect py3 changes for dict ordering and implicit
#   Enumerable wrapping
#   + 'reverse' u.test
#   + 'foreach' u.test
import itertools
#import exceptions

class Enumerable(object):
    
    def _ensureEnumerable(enumerable, argName='enumerable'):
        if not isinstance(enumerable, Enumerable):
            if hasattr(enumerable, "__iter__"):
                return Enumerable(enumerable)
            else:
                raise TypeError("the input " + argName + " must be must be an enumerable or an instance of Enumerable")
        else:
            return enumerable

    def __init__(self, data=None):
        """
        Constructor
        ** Note: no type checking of the data elements are performed during instantiation. **
        :param data: iterable object
        :return: None
        """
        if data == None:
            data = []

        if not hasattr(data, "__iter__"):
            raise TypeError("Enumerable must be instantiated with an iterable object")
        self._data = data

    def __iter__(self):
        cache = []
        for element in self._data:
            cache.append(element)
            yield element
        self._data = cache

    def __repr__(self):
        return self._data.__repr__()

    def to_list(self):
        """
        Converts the iterable into a list
        :return: list object
        """
        return list(element for element in self)

    def count(self):
        """
        Returns the number of elements in iterable
        :return: integer object
        """
        return sum(1 for element in self)
   
    def reverse(self):
        """
        Reverses the elements in iterable
        :return: new Enumerable object containing transformed data
        """
        return Enumerable(reversed(self._data))
   
    def foreach(self, action):
        """
        Iterates throug all elements an invokes the action for every single one of them.
        This method doesn't exactly follow the "immutability paradigm" but it's just sometime very convenient. 
        Usage:
            items.foreach(print)
        :return: the original iterable object
        """
        for x in self._data:
            action(x)
        return self

    def select(self, func=None):
        """
        Transforms data into different form
        :param func: lambda expression on how to perform transformation
        :return: new Enumerable object containing transformed data
        """
        if func == None:
            func = lambda x: x
        return Enumerable(map(func, self))


    def sum(self, func=None):
        """
        Returns the sum of af data elements
        :param func: lambda expression to transform data
        :return: sum of selected elements
        """
        if func == None:
            func = lambda x: x
        return sum(self.select(func))

    def min(self, func=None):
        """
        Returns the min value of data elements
        :param func: lambda expression to transform data
        :return: minimum value
        """
        if func == None:
            func = lambda x: x
        if self.count() == 0:
            raise NoElementsError("Iterable contains no elements")
        return min(self.select(func))

    def max(self, func=lambda x: x):
        """
        Returns the max value of data elements
        :param func: lambda expression to transform data
        :return: maximum value
        """
        if self.count() == 0:
            raise NoElementsError("Iterable contains no elements")
        return max(self.select(func))

    def avg(self, func=None):
        """
        Returns the average value of data elements
        :param func: lambda expression to transform data
        :return: average value as float object
        """
        if func == None:
            func = lambda x: x
        count = self.count()
        if count == 0:
            raise NoElementsError("Iterable contains no elements")
        return float(self.sum(func)) / float(count)

    def median(self, func=None):
        """
        Return the median value of data elements
        :param func: lambda expression to project and sort data
        :return: median value
        """
        if func == None:
            func = lambda x: x
        if self.count() == 0:
            raise NoElementsError("Iterable contains no elements")
        result = self.order_by(func).select(func).to_list()
        length = len(result)
        i = int(length / 2)
        return result[i] if length % 2 == 1 else (float(result[i - 1]) + float(result[i])) / float(2)

    def elementAt(self, n):
        """
        Returns element at given index.
            * Raises NoElementsError if no element found at specified position
        :param n: index as int object
        :return: Element at given index
        """
        result = list(itertools.islice(self.to_list(), max(0, n), n + 1, 1))
        if len(result) == 0:
            raise NoElementsError("No element found at index {0}".format(n))
        return result[0]

    def elementAtOrDefault(self, n):
        """
        Returns element at given index or None if no element found
            * Raises IndexError if n is greater than the number of elements in enumerable
        :param n: index as int object
        :return: Element at given index
        """
        try:
            return self.elementAt(n)
        except NoElementsError:
            return None

    def first(self, key=None):
        """
        Returns the first element
        :param func: lambda expression to test data
        :return: data element as object or NoElementsError if transformed data contains no elements
        """
        count = self.count()
        if count == 0:
            raise NoElementsError("Iterable contains no elements")

        if key:
            for item in self._data:
                if key(item):
                    return item
            raise NoElementsError("Iterable contains no elements")
        else:
            return self.elementAt(0)

    def first_or_default(self, key=None):
        """
        Return the first element
        :return: data element as object or None if transformed data contains no elements
        """
        if key :
            for item in self._data:
                if key(item):
                    return item
            return None
        else:
            return self.elementAtOrDefault(0)

    def last(self, key=None):
        """
        Return the last element
        :param func: lambda expression to test data
        :return: data element as object or NoElementsError if transformed data contains no elements
        """
        # not convinced sorting is appropriate here; thus accessing last of
        # arbitrary unsorted
        # collection would produce wrong result
        #return Enumerable(sorted(self, key=None, reverse=True)).first()
        count = self.count()
        if count == 0:
            raise NoElementsError("Iterable contains no elements")
        #result = self._data[-1]
        #return result;
        for item in reversed(self._data):
            if key is None or key(item):
                return item
        raise NoElementsError("Iterable contains no elements")
            

    def last_or_default(self, key=None):
        """
        Return the last element
        :param func: lambda expression to test data
        :return: data element as object or None if transformed data contains no elements
        """
        for item in reversed(self._data):
            if key is None or key(item):
                return item
        return None

    def order_by(self, key):
        """
        Returns new Enumerable sorted in ascending order by given key
        :param key: key to sort by as lambda expression
        :return: new Enumerable object
        """
        if key is None:
            raise NullArgumentError("No key for sorting given")
        return Enumerable(sorted(self, key=key))

    def order_by_descending(self, key):
        """
        Returns new Enumerable sorted in descending order by given key
        :param key: key to sort by as lambda expression
        :return: new Enumerable object
        """
        if key is None:
            raise NullArgumentError("No key for sorting given")
        return Enumerable(sorted(self, key=key, reverse=True))

    def skip(self, n):
        """
        Returns new Enumerable where n elements have been skipped
        :param n: Number of elements to skip as int
        :return: new Enumerable object
        """
        return Enumerable(itertools.islice(self, n, None, 1))

    def take(self, n):
        """
        Return new Enumerable where first n elements are taken
        :param n: Number of elements to take
        :return: new Enumerable object
        """
        return Enumerable(itertools.islice(self, 0, n, 1))

    def where(self, predicate):
        """
        Returns new Enumerable where elements matching predicate are selected
        :param predicate: predicate as a lambda expression
        :return: new Enumerable object
        """
        if predicate is None:
            raise NullArgumentError("No predicate given for where clause")
        return Enumerable(filter(predicate, self))

    def single(self, predicate):
        """
        Returns single element that matches given predicate.
        Raises:
            * NoMatchingElement error if no matching elements are found
            * MoreThanOneMatchingElement error if more than one matching element is found
        :param predicate: predicate as a lambda expression
        :return: Matching element as object
        """
        result = self.where(predicate).to_list()
        count = len(result)
        if count == 0:
            raise NoMatchingElement("No matching element found")
        if count > 1:
            raise MoreThanOneMatchingElement("More than one matching element found. Use where instead")
        return result[0]

    def single_or_default(self, predicate):
        """
        Return single element that matches given predicate. If no matching element is found, returns None
        Raises:
            * MoreThanOneMatchingElement error if more than one matching element is found
        :param predicate: predicate as a lambda expression
        :return: Matching element as object or None if no matches are found
        """
        try:
            return self.single(predicate)
        except NoMatchingElement:
            return None

    def select_many(self, func=None):
        """
        Flattens an iterable of iterables returning a new Enumerable
        :param func: selector as lambda expression
        :return: new Enumerable object
        """
        if func == None:
            func = lambda x: x
        return Enumerable(itertools.chain.from_iterable(self.select(func)))

    def add(self, element):
        """
        Adds an element to the enumerable.
        :param element: An element
        :return: new Enumerable object
        """
        if element is None:
            return self
        return self.concat(Enumerable([element]))

    def concat(self, enumerable):
        """
        Adds enumerable to an enumerable
        ** NOTE **
        This operation can be expensive depending on the size of the enumerable to be concatenated. This is because
        the concatenation algorithm performs type checking to ensure that the same object types are being added. If
        the self enumerable has n elements and the enumerable to be added has m elements then the type checking
        takes O(mn) time.
        :param enumerable: An iterable object
        :return: new Enumerable object
        """
        enumerable = Enumerable._ensureEnumerable(enumerable)
        
        for element in enumerable._data:
            element_type = type(element)
            if self.any(lambda x: type(x) != element_type):
                raise TypeError("type mismatch between concatenated enumerables")
        return Enumerable(itertools.chain(self._data, enumerable._data))

    def group_by(self, key_names=[], key=None, result_func=None):
        """
        Groups an enumerable on given key selector. Index of key name corresponds to index of key lambda function.

        Usage:
            Enumerable([1,2,3]).group_by(key_names=['id'], key=lambda x: x).to_list() --> Enumerable object [
                Grouping object {
                    key.id: 1,
                    _data: [1]
                },
                Grouping object {
                    key.id: 2,
                    _data: [2]
                },
                Grouping object {
                    key.id: 3,
                    _data: [3]
                }
            ]
            Thus the key names for each grouping object can be referenced through the key property. Using the above example:

            Enumerable([1,2,3]).group_by(key_names=['id'], key=lambda x: x).select(lambda g: { 'key': g.key.id, 'count': g.count() }

        :param key_names: list of key names
        :param key: key selector as lambda expression
        :return: Enumerable of grouping objects
        """
        if key == None:
            key = lambda x: x

        if result_func == None:
            result_func = lambda x: x

        result = []
        ordered = self
        try:
            ordered = sorted(self, key=key)
        except TypeError:
            pass # in Python 3 dictionaries are no longer sortable so just continue unsorted

        grouped = itertools.groupby(ordered, key)
        for k, g in grouped:
            can_enumerate = isinstance(k, list) or isinstance(k, tuple) and len(k) > 0
            key_prop = {}
            for i, prop in enumerate(key_names):
                key_prop.setdefault(prop, k[i] if can_enumerate else k)
            key_object = Key(key_prop)
            result.append(Grouping(key_object, list(g)))
        return Enumerable(result).select(result_func)

    def distinct(self, key=None):
        """
        Returns enumerable containing elements that are distinct based on given key selector
        :param key: key selector as lambda expression
        :return: new Enumerable object
        """
        if key == None:
            key = lambda x: x
        return self.group_by(key=key).select(lambda g: g.first())

    def join(self, inner_enumerable, outer_key=None, inner_key=None, result_func=None):
        """
        Return enumerable of inner equi-join between two enumerables
        :param inner_enumerable: inner enumerable to join to self
        :param outer_key: key selector of outer enumerable as lambda expression
        :param inner_key: key selector of inner enumerable as lambda expression
        :param result_func: lambda expression to transform result of join
        :return: new Enumerable object
        """
        if outer_key == None:
            outer_key = lambda x: x
        if inner_key == None:
            inner_key = lambda x: x
        if  result_func == None:
            result_func = lambda x: x

        inner_enumerable = Enumerable._ensureEnumerable(inner_enumerable, 'inner_enumerable')
        return Enumerable(itertools.product(filter(lambda x: outer_key(x) in map(inner_key, inner_enumerable), self),
                          filter(lambda y: inner_key(y) in map(outer_key, self), inner_enumerable)))\
                         .where(lambda x: outer_key(x[0]) == inner_key(x[1]))\
                         .select(result_func)

    def default_if_empty(self, value=None):
        """
        Returns an enumerable containing a single None element if enumerable is empty, otherwise the enumerable itself
        :return: an Enumerable object
        """
        if self.count() == 0:
            return Enumerable([value])
        return self

    def group_join(self, inner_enumerable, outer_key=None, inner_key=None, result_func=None):
        """
        Return enumerable of group join between two enumerables
        :param inner_enumerable: inner enumerable to join to self
        :param outer_key: key selector of outer enumerable as lambda expression
        :param inner_key: key selector of inner enumerable as lambda expression
        :param result_func: lambda expression to transform the result of group join
        :return: new Enumerable object
        """
        if outer_key == None:
            outer_key = lambda x: x
        if inner_key == None:
            inner_key = lambda x: x
        if  result_func == None:
            result_func = lambda x: x

        inner_enumerable = Enumerable._ensureEnumerable(inner_enumerable, "inner enumerable")
        return Enumerable(itertools.product(self, inner_enumerable.default_if_empty()))\
                      .group_by(key_names=['id'], \
                                key=lambda x: outer_key(x[0]), \
                                result_func=lambda g: (g.first()[0], g.where(lambda x: inner_key(x[1]) == g.key.id)\
                                                                      .select(lambda x: x[1])))\
                      .select(result_func)


    def any(self, predicate=None):
        """
        Returns true if any elements that satisfy predicate are found
        :param predicate: condition to satisfy as lambda expression
        :return: boolean True or False
        """
        if predicate is None:
            predicate=lambda x: x
        return self.where(predicate).count() > 0

    def intersect(self, enumerable, key=None):
        """
        Returns enumerable that is the intersection between given enumerable and self
        :param enumerable: enumerable object
        :param key: key selector as lambda expression
        :return: new Enumerable object
        """
        if key == None:
            key=lambda x: x
        enumerable = Enumerable._ensureEnumerable(enumerable)
        return self.join(enumerable, key, key, result_func=lambda x: x).distinct().select(lambda x: x[0])


    def union(self, enumerable, key=None):
        """
        Returns enumerable that is a union of elements between self and given enumerable
        :param enumerable: enumerable to union self to
        :param key: key selector used to determine uniqueness
        :return: new Enumerable object
        """
        if key == None:
            key=lambda x: x
        enumerable = Enumerable._ensureEnumerable(enumerable)
        return self.concat(enumerable).distinct(key)

    def except_(self, enumerable, key=None):
        """
        Returns enumerable that subtracts given enumerable elements from self
        :param enumerable: enumerable object
        :param key: key selector as lambda expression
        :return: new Enumerable object
        """
        if key == None:
            key=lambda x: x
        enumerable = Enumerable._ensureEnumerable(enumerable)
        membership = (0 if key(element) in enumerable.intersect(self).select(key) else 1 for element in self)
        return Enumerable(itertools.compress(self, membership))

    def contains(self, element, key=None):
        """
        Returns True if element is found in enumerable, otherwise False
        :param element: the element being tested for membership in enumerable
        :param key: key selector to use for membership comparison
        :return: boolean True or False
        """
        if key == None:
            key=lambda x: x
        return self.select(key).any(lambda x: x == key(element))

class Key(object):
    def __init__(self, key, **kwargs):
        """
        Constructor for Key class. Autogenerates key properties in object given dict or kwargs
        :param key: dict of name-values
        :param kwargs: optional keyword arguments
        :return: void
        """
        key = key if key is not None else kwargs
        self.__dict__.update(key)

    def __repr__(self):
        return self.__dict__.__repr__()

class Grouping(Enumerable):
    def __init__(self, key, data):
        """
        Constructor of Grouping class used for group by operations of Enumerable class
        :param key: Key instance
        :param data: iterable object
        :return: void
        """
        if not isinstance(key, Key):
            raise Exception("key argument should be a Key instance")
        self.key = key
        super(Grouping, self).__init__(data)

    def __repr__(self):
        return {
            'key': self.key.__repr__(),
            'enumerable': self._data.__repr__()
        }.__repr__()

class NoElementsError(Exception): pass
class NullArgumentError(Exception): pass
class NoMatchingElement(Exception): pass
class MoreThanOneMatchingElement(Exception): pass


class qlist(Enumerable): 
    """
        Short named version of py_linq.Enumerable. It stands for 'queryable list'.
    """
    def __init__(self, data=[]): 
        super().__init__(data)
        pass