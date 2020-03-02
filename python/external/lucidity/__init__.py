# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os
import uuid
import imp

from ._version import __version__
from .template import Template, Resolver
from .error import ParseError, FormatError, NotFound


def discover_templates(paths=None, recursive=True):
    '''Search *paths* for mount points and load templates from them.

    *paths* should be a list of filesystem paths to search for mount points.
    If not specified will try to use value from environment variable
    :envvar:`LUCIDITY_TEMPLATE_PATH`.

    A mount point is a Python file that defines a 'register' function. The
    function should return a list of instantiated
    :py:class:`~lucidity.template.Template` objects.

    If *recursive* is True (the default) then all directories under a path
    will also be searched.

    '''
    templates = []

    if paths is None:
        paths = os.environ.get('LUCIDITY_TEMPLATE_PATH', '').split(os.pathsep)

    for path in paths:
        for base, directories, filenames in os.walk(path):
            for filename in filenames:
                _, extension = os.path.splitext(filename)
                if extension != '.py':
                    continue

                module_path = os.path.join(base, filename)
                module_name = uuid.uuid4().hex
                module = imp.load_source(module_name, module_path)
                try:
                    registered = module.register()
                except AttributeError:
                    pass
                else:
                    if registered:
                        templates.extend(registered)

            if not recursive:
                del directories[:]

    return templates


def parse(path, templates):
    '''Parse *path* against *templates*.

    *path* should be a string to parse.

    *templates* should be a list of :py:class:`~lucidity.template.Template`
    instances in the order that they should be tried.

    Return ``(data, template)`` from first successful parse.

    Raise :py:class:`~lucidity.error.ParseError` if *path* is not
    parseable by any of the supplied *templates*.

    '''
    for template in templates:
        try:
            data = template.parse(path)
        except ParseError:
            continue
        else:
            return (data, template)

    raise ParseError(
        'Path {0!r} did not match any of the supplied template patterns.'
        .format(path)
    )


def format(data, templates):  # @ReservedAssignment
    '''Format *data* using *templates*.

    *data* should be a dictionary of data to format into a path.

    *templates* should be a list of :py:class:`~lucidity.template.Template`
    instances in the order that they should be tried.

    Return ``(path, template)`` from first successful format.

    Raise :py:class:`~lucidity.error.FormatError` if *data* is not
    formattable by any of the supplied *templates*.


    '''
    for template in templates:
        try:
            path = template.format(data)
        except FormatError:
            continue
        else:
            return (path, template)

    raise FormatError(
        'Data {0!r} was not formattable by any of the supplied templates.'
        .format(data)
    )


def get_template(name, templates):
    '''Retrieve a template from *templates* by *name*.

    Raise :py:exc:`~lucidity.error.NotFound` if no matching template with
    *name* found in *templates*.

    '''
    for template in templates:
        if template.name == name:
            return template

    raise NotFound(
        '{0} template not found in specified templates.'.format(name)
    )
