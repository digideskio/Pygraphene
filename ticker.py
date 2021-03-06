
import math

class Locator(object):
    """
    A generic class that defines the locations for ticks.

    Different Locator subclasses can have different pertinent data
    (LinearLocator needs to know the number of ticks it should
    provide, whereas StaticLocator needs to have a list of the specific
    locations for the ticks). This pertinent data can be updated either
    via the appropriate set___ method, or the generic setValues method.
    If the setValues method is used, the user must pass in keyword arguments
    for each datum to update. The accepted keyword arguments are listed
    in the individual setValues methods.
    """

    def __init__(self):
        pass

    def setValues(self, **kwargs):
        """
        Set internal values based on the keywords given. If a keyword
        does not correspond to a value for a specific subclass, then
        it is ignored.
        """
        pass

class NullLocator(Locator):
    """
    Provides no locations.
    """

    def locations(self, start, end, axisType='major'):
        return []

class LinearLocator(Locator):
    """
    Define tick locations by evenly spacing a certain number of ticks over the data range.
    """

    def __init__(self, num=5):
        """
        **Constructor**
        
        num
            The number of ticks that should be created.
        """

        Locator.__init__(self)

        # in case someone passes in a non-int, we will still have a default
        self._num = 5
        self.setNum(num)

    def setNum(self, num):
        """
        Set the number of ticks to create locations for.
        """
        if isinstance(num, int):
            self._num = num

    def locations(self, start, end, axisType='major'):
        """
        Return a list of data coordinates between start and end,
        evenly spaced so that there are num values.
        """

        num = self._num

        if axisType == 'minor':
            num += 2

        delta = (float(end) - float(start)) / float(num - 1)

        locs = []

        # If the last location is start + num*delta, we could get a roundoff
        # error and the last location is not displayed. So we add the delta
        # for all but the last location, and use end as the last one.
        for i in range(num - 1):
            locs.append(start)
            start += delta

        locs.append(end)

        return locs

    def setValues(self, **kwargs):
        """
        Accepted keywords:
        
        * num

        """
        num = kwargs.pop('num', None)
        self.setNum(num)

class FixedLocator(Locator):
    """
    Define tick locations with a list of values that are passed in.
    """

    def __init__(self, locations=[], nTicks=None):
        """
        **Constructor**

        locations
            The locations that ticks should be found at. Must be a list, but
            not necessarily of numbers.
        nTicks
            How many ticks should be provided. Must be either None or an
            integer. If nTicks is None, then
            all locations will be provided. If nTicks < 2, then 2 location
            will be provided.
        """

        Locator.__init__(self)

        self._locations = []
        self.setLocations(locations)
        self.setNTicks(nTicks)

    def setLocations(self, locations):
        """
        Set the locations for the ticks. The passed locations will be
        sorted by number.
        """

        if isinstance(locations, list) or isinstance(locations, tuple):
            self._locations = locations

    def setNTicks(self, nTicks):
        """
        Set nTicks.
        """

        if nTicks is None:
            self._nTicks = None
        elif isinstance(nTicks, int):
            if nTicks < 2:
                self._nTicks = 2
            else:
                self._nTicks = nTicks

    def locations(self, start, end, axisType='major'):
        """
        Return the list of locations, subsampled if nTicks is not None.

        Disregards the start and end parameters.
        """
# TODO should subsample such that the min. value is always displayed
# TODO have not tested this with minor axes

        # Do not subsample
        if self._nTicks is None or self._nTicks >= len(self._locations):
            return self._locations

        # Subsample. Always include the two end values in the locations list
        if self._nTicks < 2:
            self._nTicks = 2
        n = self._nTicks - 1

        locs = []

        subsamplingDistance = float(len(self._locations) - 1) / float(n)

        for i in range(n):
            locs.append(self._locations[int(round(i * subsamplingDistance))])

        locs.append(self._locations[-1])

        return locs

    def setValues(self, **kwargs):
        """
        Accepted keywords:

        * locations
        * nTicks

        """

        keys = kwargs.keys()

        if 'locations' in keys:
            self.setLocations(kwargs['locations'])
        if 'nTicks' in keys:
            self.setNTicks(kwargs['nTicks'])

class SpacedLocator(Locator):
    """
    Define tick locations by spacing ticks by 'base'. If 'anchor' is specified,
    then ticks will be spaced starting from there instead of from the starting
    edge of the axis.
    """

    def __init__(self, base=1.0, anchor=None):
        """
        **Constructor**

        base
            The spacing in the data coordinates between ticks.

        anchor
            Where to anchor the ticks. Can be a number or None.
        """

        Locator.__init__(self)

        # in case someone passes in a non-num, we will still have a default
        self._base = 1.0
        self._anchor = None
        self.setBase(base)
        self.setAnchor(anchor)

    def setBase(self, base):
        """
        Set the base. base must be a positive int or float.
        """
        if isinstance(base, int) or isinstance(base, float):
            if base > 0:
                self._base = base

    def setAnchor(self, anchor):
        """
        Set the anchor. anchor must be an int, float, or None.
        """
        if isinstance(anchor, int) or isinstance(anchor, float) or anchor is None:
            self._anchor = anchor

    def locations(self, start, end, axisType='major'):
        """
        Return a list of data coordinates between start and end,
        spaced by base.

        If anchor is None, then the locations start at 'start' and end
        at the first location >= 'end'.

        If anchor is specified, then the ticks are spaced off of the anchor
        value. The closed values beyond or equal to 'start' and 'end' will
        be included.
        """

        base = self._base
        anchor = self._anchor
        locs = []
        if anchor is None:
            loc = start

            while loc < end:
                locs.append(loc)
                loc += base

            locs.append(loc)

        # use anchor
        else:
            loc = anchor
            while loc > start:
                locs.insert(0, loc)
                loc -= base

            locs.insert(0, loc)

            loc = anchor + base
            while loc < end:
                locs.append(loc)
                loc += base

            locs.append(loc)

        return locs

    def setValues(self, **kwargs):
        """
        Accepted keywords:

        * base
        * anchor

        """
        base = kwargs.pop('base', None)
        anchor = kwargs.pop('anchor', '')  # None is a valid value, so need '' for nothing to happen
        self.setBase(base)
        self.setAnchor(anchor)

class LogLocator(Locator):
    """
    Define tick locations in a logarithmic fashion.
    """

# TODO need to take care of symlog

    def __init__(self, base=10, subdivisions=[1]):
        """
        **Constructor**

        base
            The base of the logarithm. Defaults to 10.

        subdivisions
            The list of locations within one order of magnitude that should
            be created. If [1,2,5], then, for example, the following would
            be locations in [1, 100]: [1, 2, 5, 10, 20, 50, 100].
        """

        Locator.__init__(self)

        self._base = 10
        self.setBase(base)
        self._subdivisions = [1]
        self.setSubdivisions(subdivisions)

    def setBase(self, base):
        """
        Set the base of the logarithm.
        """
        if isinstance(base, int) or isinstance(base, float):
            self._base = base

    def setSubdivisions(self, subdivisions):
        """
        Set the subdivisions of the logarithm.
        """
        if isinstance(subdivisions, list) or isinstance(subdivisions, tuple):
            self._subdivisions = list(subdivisions)

    def locations(self, start, end, axisType='major'):
        """
        If axisType is major, then return the orders of magnitude between
        start and end. If axisType is minor, then return the subdivisions.
        """

        locs = []

        try:
            exponent = int(math.floor(math.log(start, self._base)))
        except ValueError:
            # input is < 0, default to 1
            exponent = 0
        try:
            lastExponent = int(math.ceil(math.log(end, self._base)))
        except ValueError:
            # input is < 0, default to 1
            lastExponent = 0
        
        while exponent <= lastExponent:
            locs.extend([x * pow(self._base, exponent) for x in self._subdivisions])
            exponent += 1
        
        return locs

    def setValues(self, **kwargs):
        """
        Accepted keywords:
        
        * base

        """
        base = kwargs.pop('base', None)
        subdivisions = kwargs.pop('subdivisions', None)
        self.setBase(base)
        self.setSubdivisions(subdivisions)


# TODO it doesn't seem like labeler needs to be instantiated. maybe it does when given
# a list of values to print out, instead of using the locations given to it
class Labeler(object):
    """
    A generic class that defines the labels for ticks.
    """

    def __init__(self):
        pass
    
    def labels(self, locations):
        """
        Must return a list with exactly the same length as locations.
        """
        pass

    def setValues(self, **kwargs):
        """
        Set internal values based on the keywords given. If a keyword
        does not correspond to a value for a specific subclass, then
        it is ignored.
        """
        pass

class NullLabeler(Labeler):
    """
    No labels.
    """
    def labels(self, locations):
        return [''] * len(locations)

class StringLabeler(Labeler):
    """
    Labels that are manually specified by the user.

    If the user specifies fewer labels than the number of locations that
    are requested, then empty strings are added. If there are too many
    labels, then the label list is truncated.
    """

    def __init__(self, labels=[]):
        self._labels = []
        self.setLabels(labels)

    def setLabels(self, labels):
        if isinstance(labels, list) or isinstance(labels, tuple):
            self._labels = list(labels)

    def labels(self, locations):
        locsLength = len(locations)
        labelsLength = len(self._labels)

        strings = []
        if locsLength == labelsLength:
            strings.extend(self._labels)
        elif locsLength > labelsLength:
            strings.extend(self._labels)
            strings.extend([''] * (locsLength - labelsLength))
        elif locsLength < labelsLength:
            strings.extend(self._labels[:locsLength])

        return map(str, strings)

class FormatLabeler(Labeler):
    """
    Labels that are the same as the location value.

    Optionally, a format string can be specified. This should follow the
    python format string specifications. Defaults to None, in which case
    the locations are just converted directly to strings.
    """

    def __init__(self, fmt=None):
        self._fmt = None
        self.setFormatter(fmt)

    def setFormatter(self, fmt):
        if isinstance(fmt, str) or fmt is None:
            self._fmt = fmt

    def labels(self, locations):
        strings = map(str, locations)
        if self._fmt is not None:
            strings = map(lambda loc: self._fmt % loc, locations)

        return strings

class NullLabeler(Labeler):
    """
    Labels that are blank strings.
    """

    def labels(self, locations):
        return [''] * len(locations)

