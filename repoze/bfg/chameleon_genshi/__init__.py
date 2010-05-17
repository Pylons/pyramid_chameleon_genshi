import sys

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

