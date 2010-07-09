import sys
import os
import pkg_resources

from webob import Response

from zope.interface import implements

try:
    from chameleon.genshi.template import GenshiTemplateFile
except ImportError: # pragma: no cover
    exc_class, exc, tb = sys.exc_info()
    # Chameleon doesn't work on non-CPython platforms
    class GenshiTemplateFile(object):
        def __init__(self, *arg, **kw):
            raise ImportError, exc, tb

from repoze.bfg.interfaces import IChameleonTranslate
from repoze.bfg.interfaces import IResponseFactory
from repoze.bfg.interfaces import ITemplateRenderer

from repoze.bfg.decorator import reify
from repoze.bfg.renderers import template_renderer_factory
from repoze.bfg.settings import get_settings
from repoze.bfg.threadlocal import get_current_registry

def renderer_factory(path):
    return template_renderer_factory(path, GenshiTemplateRenderer)

class GenshiTemplateRenderer(object):
    implements(ITemplateRenderer)
    def __init__(self, path):
        self.path = path

    @reify # avoid looking up reload_templates before manager pushed
    def template(self):
        settings = get_settings()
        debug = False
        auto_reload = False
        if settings:
            # using .get here is a strategy to be kind to old *tests* rather
            # than being kind to any existing production system
            auto_reload = settings.get('reload_templates')
            debug = settings.get('debug_templates')
        reg = get_current_registry()
        translate = None
        if reg is not None:
            translate = reg.queryUtility(IChameleonTranslate)
        return GenshiTemplateFile(self.path,
                                  auto_reload=auto_reload,
                                  debug=debug,
                                  translate=translate)

    def implementation(self):
        return self.template
    
    def __call__(self, value, system):
        try:
            system.update(value)
        except (TypeError, ValueError):
            raise ValueError('renderer was passed non-dictionary as value')
        result = self.template(**system)
        return result

def get_renderer(path):
    """ Return a callable object which can be used to render a
    :term:`Chameleon` ZPT template using the template implied by the
    ``path`` argument.  The ``path`` argument may be a
    package-relative path, an absolute path, or a :term:`resource
    specification`."""
    return renderer_factory(path)

def get_template(path):
    """ Return the underlying object representing a :term:`Chameleon`
    ZPT template using the template implied by the ``path`` argument.
    The ``path`` argument may be a package-relative path, an absolute
    path, or a :term:`resource specification`."""
    renderer = renderer_factory(path)
    return renderer.implementation()

def render_template(path, **kw):
    """ Render a :term:`Chameleon` ZPT template using the template
    implied by the ``path`` argument.  The ``path`` argument may be a
    package-relative path, an absolute path, or a :term:`resource
    specification`.  The arguments in ``*kw`` are passed as top-level
    names to the template, and so may be used within the template
    itself.  Returns a string."""
    renderer = renderer_factory(path)
    return renderer(kw, {})

def render_template_to_response(path, **kw):
    """ Render a :term:`Chameleon` ZPT template using the template
    implied by the ``path`` argument.  The ``path`` argument may be a
    package-relative path, an absolute path, or a :term:`resource
    specification`.  The arguments in ``*kw`` are passed as top-level
    names to the template, and so may be used within the template
    itself.  Returns a :term:`Response` object with the body as the
    template result.."""
    renderer = renderer_factory(path)
    result = renderer(kw, {})
    reg = get_current_registry()
    response_factory = reg.queryUtility(IResponseFactory, default=Response)
    return response_factory(result)

class XIncludes(object):
    """Dynamic XInclude registry providing a ``get``-method that will
    resolve a filename to a template instance. Format must be
    explicitly provided."""
    
    def __init__(self, registry, relpath, factory):
        self.registry = registry
        self.relpath = relpath
        self.factory = factory

    def get(self, filename, format):
        if not os.path.isabs(filename):
            if ':' in filename:
                # it's a resource spec
                filename = abspath_from_resource_spec(filename)
            else:
                # it's a relative filename
                filename = os.path.join(self.relpath, filename)
        filename = os.path.realpath(filename)
        template = self.registry.get(filename)
        if template is not None:
            return template
        return self.factory(filename, format=format)

    @classmethod
    def activate(cls):
        from chameleon.core.template import TemplateFile
        TemplateFile.xincludes_class = cls # monkey patch ourselves in

def resolve_resource_spec(spec, pname='__main__'):
    if os.path.isabs(spec):
        return None, spec
    filename = spec
    if ':' in spec:
        pname, filename = spec.split(':', 1)
    elif pname is None:
        pname, filename = None, spec
    return pname, filename

def abspath_from_resource_spec(spec, pname='__main__'):
    if pname is None:
        return spec
    pname, filename = resolve_resource_spec(spec, pname)
    if pname is None:
        return filename
    return pkg_resources.resource_filename(pname, filename)
