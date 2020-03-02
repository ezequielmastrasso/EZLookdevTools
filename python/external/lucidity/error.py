# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

'''Custom error classes.'''


class ParseError(Exception):
    '''Raise when a template is unable to parse a path.'''


class FormatError(Exception):
    '''Raise when a template is unable to format data into a path.'''


class NotFound(Exception):
    '''Raise when an item cannot be found.'''


class ResolveError(Exception):
    '''Raise when a template reference can not be resolved.'''
