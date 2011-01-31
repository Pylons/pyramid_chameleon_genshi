import sys
import os
import pkg_resources

from zope.interface import implements

try:
    from chameleon.genshi.template import GenshiTemplateFile
except ImportError: # pragma: no cover
    exc_class, exc, tb = sys.exc_info()
    # Chameleon doesn't work on non-CPython platforms
    class GenshiTemplateFile(object):
        def __init__(self, *arg, **kw):
            raise ImportError, exc, tb

from pyramid.interfaces import ITemplateRenderer

from pyramid.decorator import reify
from pyramid.path import caller_package
from pyramid import renderers

def renderer_factory(path):
    return renderers.template_renderer_factory(path, GenshiTemplateRenderer)

class GenshiTemplateRenderer(object):
    implements(ITemplateRenderer)
    def __init__(self, path, lookup):
        self.path = path
        self.lookup = lookup

    @reify # avoid looking up reload_templates before manager pushed
    def template(self):
        if sys.platform.startswith('java'): # pragma: no cover
            raise RuntimeError(
                'Chameleon templates are not compatible with Jython')
        return GenshiTemplateFile(self.path,
                                  auto_reload=self.lookup.auto_reload,
                                  debug = self.lookup.debug,
                                  translate = self.lookup.translate)

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
    specification`.

    .. warning:: This API is deprecated in :mod:`pyramid_chameleon_genshi`
       1.0.  Use :func:`pyramid.renderers.get_renderer` instead.
    """
    package = caller_package()
    factory = renderers.RendererHelper(name=path, package=package)
    return factory.get_renderer()

def get_template(path):
    """ Return the underlying object representing a :term:`Chameleon`
    ZPT template using the template implied by the ``path`` argument.
    The ``path`` argument may be a package-relative path, an absolute
    path, or a :term:`resource specification`.

        .. warning:: This API is deprecated in :mod:`pyramid_chameleon_genshi`
       1.0.  Use :func:`pyramid.renderers.get_renderer` instead.
    """
    package = caller_package()
    factory = renderers.RendererHelper(name=path, package=package)
    return factory.get_renderer().implementation()

def render_template(path, **kw):
    """ Render a :term:`Chameleon` ZPT template using the template
    implied by the ``path`` argument.  The ``path`` argument may be a
    package-relative path, an absolute path, or a :term:`resource
    specification`.  The arguments in ``*kw`` are passed as top-level
    names to the template, and so may be used within the template
    itself.  Returns a string.

    .. warning:: This API is deprecated in :mod:`pyramid_chameleon_genshi`
       1.0.  Use :func:`pyramid.renderers.get_renderer` instead.
    """
    package = caller_package()
    request = kw.pop('request', None)
    renderer = renderers.RendererHelper(name=path, package=package)
    return renderer.render(kw, None, request=request)

def render_template_to_response(path, **kw):
    """ Render a :term:`Chameleon` ZPT template using the template
    implied by the ``path`` argument.  The ``path`` argument may be a
    package-relative path, an absolute path, or a :term:`resource
    specification`.  The arguments in ``*kw`` are passed as top-level
    names to the template, and so may be used within the template
    itself.  Returns a :term:`Response` object with the body as the
    template result.

    .. warning:: This API is deprecated in :mod:`pyramid_chameleon_genshi`
       1.0.  Use :func:`pyramid.renderers.get_renderer` instead.
    """
    package = caller_package()
    request = kw.pop('request', None)
    renderer = renderers.RendererHelper(name=path, package=package)
    return renderer.render_to_response(kw, None, request=request)

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
        filename = os.path.normpath(filename)
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

def includeme(config):
    config.add_renderer('.genshi', renderer_factory)
    
