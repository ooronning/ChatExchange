import sys
from html.parser import HTMLParser
from html import entities as htmlentitydefs
import functools
import logging
import weakref


def parse_age_ago(text):
    suffixes = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
        'y': 31536000
    }
    if text == "n/a":
        return -1  # Take this as an error code if you want
    if text == "just now":
        return 0
    splat = text.split(' ')
    assert len(splat) == 2, "text doesn't appear to be in <x ago> format"
    char = splat[0][-1]
    number = int(splat[0][:-1])
    assert char in suffixes, "suffix char unrecognized"
    return timedelta(seconds=number * suffixes[char])


class LazyFrom(object):
    """
    A descriptor used when multiple lazy attributes depend on a common
    source of data.
    """
    def __init__(self, method_name):
        """
        method_name is the name of the method that will be invoked if
        the value is not known. It must assign a value for the attribute
        attribute (through this descriptor).
        """
        self.method_name = method_name
        self.values = weakref.WeakKeyDictionary()

    def __get__(self, obj, cls):
        if obj is None:
            return self

        if obj not in self.values:
            method = getattr(obj, self.method_name)
            method()

        assert obj in self.values, "method failed to populate attribute"

        return self.values[obj]

    def __set__(self, obj, value):
        self.values[obj] = value

    def __delete__(self, obj):
        if obj in self.values:
            del self.values[obj]
