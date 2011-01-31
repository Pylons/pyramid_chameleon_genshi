import unittest

class Base(object):
    def setUp(self):
        from pyramid.testing import setUp
        from pyramid.registry import Registry
        registry = Registry()
        self.config = setUp(registry=registry)

    def tearDown(self):
        from pyramid.testing import tearDown
        tearDown()

    def _getTemplatePath(self, name):
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(here, 'fixtures', name)

    def _registerUtility(self, utility, iface, name=''):
        from pyramid.threadlocal import get_current_registry
        reg = get_current_registry()
        reg.registerUtility(utility, iface, name=name)
        return reg

    def _registerRenderer(self):
        from pyramid_chameleon_genshi import renderer_factory
        self.config.add_renderer('.genshi', renderer_factory)
        

class GenshiTemplateRendererTests(Base, unittest.TestCase):
    def _getTargetClass(self):
        from pyramid_chameleon_genshi import GenshiTemplateRenderer
        return GenshiTemplateRenderer

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_instance_implements_ITemplate(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import ITemplateRenderer
        path = self._getTemplatePath('minimal.genshi')
        lookup = DummyLookup()
        verifyObject(ITemplateRenderer, self._makeOne(path, lookup))

    def test_class_implements_ITemplate(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import ITemplateRenderer
        verifyClass(ITemplateRenderer, self._getTargetClass())

    def test_call(self):
        minimal = self._getTemplatePath('minimal.genshi')
        lookup = DummyLookup()
        instance = self._makeOne(minimal, lookup)
        result = instance({}, {})
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result,
                     '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>')

    def test_template_reified(self):
        minimal = self._getTemplatePath('minimal.genshi')
        lookup = DummyLookup()
        instance = self._makeOne(minimal, lookup)
        self.failIf('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template, instance.__dict__['template'])

    def test_template_with_ichameleon_translate(self):
        minimal = self._getTemplatePath('minimal.genshi')
        lookup = DummyLookup()
        instance = self._makeOne(minimal, lookup)
        self.failIf('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.translate, lookup.translate)

    def test_template_with_debug_templates(self):
        minimal = self._getTemplatePath('minimal.genshi')
        lookup = DummyLookup()
        lookup.debug = True
        instance = self._makeOne(minimal, lookup)
        self.failIf('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.debug, True)

    def test_template_with_reload_templates(self):
        minimal = self._getTemplatePath('minimal.genshi')
        lookup = DummyLookup()
        lookup.auto_reload = True
        instance = self._makeOne(minimal, lookup)
        self.failIf('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.auto_reload, True)

    def test_template_without_reload_templates(self):
        minimal = self._getTemplatePath('minimal.genshi')
        lookup = DummyLookup()
        lookup.auto_reload = False
        instance = self._makeOne(minimal, lookup)
        self.failIf('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.auto_reload, False)

    def test_call_with_nondict_value(self):
        minimal = self._getTemplatePath('minimal.genshi')
        lookup = DummyLookup()
        instance = self._makeOne(minimal, lookup)
        self.assertRaises(ValueError, instance, None, {})

    def test_implementation(self):
        minimal = self._getTemplatePath('minimal.genshi')
        lookup = DummyLookup()
        instance = self._makeOne(minimal, lookup)
        result = instance.implementation()()
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result,
                     '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>')
        

class RenderTemplateTests(Base, unittest.TestCase):
    def _callFUT(self, name, **kw):
        from pyramid_chameleon_genshi import render_template
        return render_template(name, **kw)

    def test_it(self):
        self._registerRenderer()
        minimal = self._getTemplatePath('minimal.genshi')
        result = self._callFUT(minimal)
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result,
                     '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>')

class RenderTemplateToResponseTests(Base, unittest.TestCase):
    def _callFUT(self, name, **kw):
        from pyramid_chameleon_genshi import render_template_to_response
        return render_template_to_response(name, **kw)

    def test_it(self):
        self._registerRenderer()
        minimal = self._getTemplatePath('minimal.genshi')
        result = self._callFUT(minimal)
        from webob import Response
        self.failUnless(isinstance(result, Response))
        self.assertEqual(result.app_iter,
                     ['<div xmlns="http://www.w3.org/1999/xhtml">\n</div>'])
        self.assertEqual(result.status, '200 OK')
        self.assertEqual(len(result.headerlist), 2)

    def test_iresponsefactory_override(self):
        self._registerRenderer()
        from webob import Response
        class Response2(Response):
            pass
        from pyramid.interfaces import IResponseFactory
        self._registerUtility(Response2, IResponseFactory)
        minimal = self._getTemplatePath('minimal.genshi')
        result = self._callFUT(minimal)
        self.failUnless(isinstance(result, Response2))

class GetRendererTests(Base, unittest.TestCase):
    def _callFUT(self, name):
        from pyramid_chameleon_genshi import get_renderer
        return get_renderer(name)

    def test_it(self):
        self._registerRenderer()
        from pyramid.interfaces import IRendererFactory
        class Dummy:
            template = object()
            def implementation(self): pass
        renderer = Dummy()
        def rf(spec):
            return renderer
        self._registerUtility(rf, IRendererFactory, name='foo')
        result = self._callFUT('foo')
        self.failUnless(result is renderer)

class GetTemplateTests(Base, unittest.TestCase):
    def _callFUT(self, name):
        from pyramid_chameleon_genshi import get_template
        return get_template(name)

    def test_it(self):
        self._registerRenderer()
        from pyramid.interfaces import IRendererFactory
        class Dummy:
            template = object()
            def implementation(self):
                return self.template
        renderer = Dummy()
        def rf(spec):
            return renderer
        self._registerUtility(rf, IRendererFactory, name='foo')
        result = self._callFUT('foo')
        self.failUnless(result is renderer.template)
        
        
class Test_resolve_resource_spec(unittest.TestCase):
    def _callFUT(self, spec, package_name='__main__'):
        from pyramid_chameleon_genshi import resolve_resource_spec
        return resolve_resource_spec(spec, package_name)

    def test_abspath(self):
        import os
        here = os.path.dirname(__file__)
        path = os.path.abspath(here)
        package_name, filename = self._callFUT(path, 'apackage')
        self.assertEqual(filename, path)
        self.assertEqual(package_name, None)

    def test_rel_spec(self):
        pkg = 'pyramid_chameleon_genshi.tests'
        path = 'test_resource.py'
        package_name, filename = self._callFUT(path, pkg)
        self.assertEqual(package_name, 'pyramid_chameleon_genshi.tests')
        self.assertEqual(filename, 'test_resource.py')
        
    def test_abs_spec(self):
        pkg = 'pyramid_chameleon_genshi.tests'
        path = 'pyramid_chameleon_genshi.nottests:test_resource.py'
        package_name, filename = self._callFUT(path, pkg)
        self.assertEqual(package_name, 'pyramid_chameleon_genshi.nottests')
        self.assertEqual(filename, 'test_resource.py')

    def test_package_name_is_None(self):
        pkg = None
        path = 'test_resource.py'
        package_name, filename = self._callFUT(path, pkg)
        self.assertEqual(package_name, None)
        self.assertEqual(filename, 'test_resource.py')
        
class Test_abspath_from_resource_spec(unittest.TestCase):
    def _callFUT(self, spec, pname='__main__'):
        from pyramid_chameleon_genshi import abspath_from_resource_spec
        return abspath_from_resource_spec(spec, pname)

    def test_pname_is_None_before_resolve_resource_spec(self):
        result = self._callFUT('abc', None)
        self.assertEqual(result, 'abc')

    def test_pname_is_None_after_resolve_resource_spec(self):
        result = self._callFUT('/abc', '__main__')
        self.assertEqual(result, '/abc')

    def test_pkgrelative(self):
        import os
        here = os.path.dirname(__file__)
        path = os.path.abspath(here)
        result = self._callFUT('abc', 'pyramid_chameleon_genshi.tests')
        self.assertEqual(result, os.path.join(path, 'abc'))

class Test_includeme(unittest.TestCase):
    def _callFUT(self, config):
        from pyramid_chameleon_genshi import includeme
        includeme(config)

    def test_it(self):
        from pyramid_chameleon_genshi import renderer_factory
        class DummyConfigurator(object):
            def __init__(self):
                self.renderers = {}

            def add_renderer(self, name, impl):
                self.renderers[name] = impl

        config = DummyConfigurator()
        self._callFUT(config)
        self.assertEqual(config.renderers['.genshi'], renderer_factory)
        

class TestXIncludes(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid_chameleon_genshi import XIncludes
        return XIncludes

    def _makeOne(self, registry=None, relpath=None, factory=None):
        if registry is None:
            registry = {}
        cls = self._getTargetClass()
        return cls(registry, relpath, factory)

    def test_get_isabs(self):
        expected_filename = '/foo/bar'
        expected_format = 'format'
        expected_result = 'abc'
        def factory(filename, format):
            self.assertEqual(filename, expected_filename)
            self.assertEqual(format, expected_format)
            return expected_result
        xi = self._makeOne(factory=factory)
        result = xi.get(expected_filename, expected_format)
        self.assertEqual(result, expected_result)
        
    def test_get_isrelpath(self):
        expected_filename = '/foo/bar'
        expected_format = 'format'
        expected_result = 'abc'
        def factory(filename, format):
            self.assertEqual(filename, expected_filename)
            self.assertEqual(format, expected_format)
            return expected_result
        xi = self._makeOne(relpath='/foo', factory=factory)
        result = xi.get('bar', expected_format)
        self.assertEqual(result, expected_result)
        
    def test_get_isresource_spec(self):
        import os
        here = os.path.dirname(__file__)
        expected_filename = os.path.join(here, 'abc')
        expected_format = 'format'
        expected_result = 'abc'
        def factory(filename, format):
            self.assertEqual(filename, expected_filename)
            self.assertEqual(format, expected_format)
            return expected_result
        xi = self._makeOne(factory = factory)
        result = xi.get('pyramid_chameleon_genshi.tests:abc',
                        expected_format)
        self.assertEqual(result, expected_result)
        
    def test_get_already_in_registry(self):
        expected_filename = '/foo/bar'
        expected_format = 'format'
        expected_result = 'template'
        xi = self._makeOne(registry={'/foo/bar':'template'})
        result = xi.get(expected_filename, expected_format)
        self.assertEqual(result, expected_result)

    def test_activate(self):
        from chameleon.core.template import TemplateFile
        original_xinclude_cls = TemplateFile.xincludes_class
        try:
            cls = self._getTargetClass()
            cls.activate()
            self.assertEqual(TemplateFile.xincludes_class, cls)
        finally:
            TemplateFile.xinclude_class = original_xinclude_cls

class DummyLookup(object):
    auto_reload=True
    debug = True
    def translate(self, msg): pass
