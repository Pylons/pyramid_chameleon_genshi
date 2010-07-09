import unittest

from repoze.bfg.testing import cleanUp

class Base(object):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTemplatePath(self, name):
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(here, 'fixtures', name)

    def _registerUtility(self, utility, iface, name=''):
        from repoze.bfg.threadlocal import get_current_registry
        reg = get_current_registry()
        reg.registerUtility(utility, iface, name=name)
        return reg
        
class GenshiTemplateRendererTests(Base, unittest.TestCase):
    def setUp(self):
        from repoze.bfg.configuration import Configurator
        from repoze.bfg.registry import Registry
        registry = Registry()
        self.config = Configurator(registry=registry)
        self.config.begin()

    def tearDown(self):
        self.config.end()

    def _getTargetClass(self):
        from repoze.bfg.chameleon_genshi import GenshiTemplateRenderer
        return GenshiTemplateRenderer

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_instance_implements_ITemplate(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ITemplateRenderer
        path = self._getTemplatePath('minimal.genshi')
        verifyObject(ITemplateRenderer, self._makeOne(path))

    def test_class_implements_ITemplate(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import ITemplateRenderer
        verifyClass(ITemplateRenderer, self._getTargetClass())

    def test_call(self):
        minimal = self._getTemplatePath('minimal.genshi')
        instance = self._makeOne(minimal)
        result = instance({}, {})
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result,
                     '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>')

    def test_template_reified(self):
        minimal = self._getTemplatePath('minimal.genshi')
        instance = self._makeOne(minimal)
        self.failIf('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template, instance.__dict__['template'])

    def test_template_with_ichameleon_translate(self):
        from repoze.bfg.interfaces import IChameleonTranslate
        def ct(): pass
        self.config.registry.registerUtility(ct, IChameleonTranslate)
        minimal = self._getTemplatePath('minimal.genshi')
        instance = self._makeOne(minimal)
        self.failIf('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.translate, ct)

    def test_template_with_debug_templates(self):
        self.config.add_settings({'debug_templates':True})
        minimal = self._getTemplatePath('minimal.genshi')
        instance = self._makeOne(minimal)
        self.failIf('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.debug, True)

    def test_template_with_reload_templates(self):
        self.config.add_settings({'reload_templates':True})
        minimal = self._getTemplatePath('minimal.genshi')
        instance = self._makeOne(minimal)
        self.failIf('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.auto_reload, True)

    def test_template_with_emptydict(self):
        from repoze.bfg.interfaces import ISettings
        self.config.registry.registerUtility({}, ISettings)
        minimal = self._getTemplatePath('minimal.genshi')
        instance = self._makeOne(minimal)
        self.failIf('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.auto_reload, False)
        self.assertEqual(template.debug, False)

    def test_call_with_nondict_value(self):
        minimal = self._getTemplatePath('minimal.genshi')
        instance = self._makeOne(minimal)
        self.assertRaises(ValueError, instance, None, {})

    def test_implementation(self):
        minimal = self._getTemplatePath('minimal.genshi')
        instance = self._makeOne(minimal)
        result = instance.implementation()()
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result,
                     '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>')
        

class RenderTemplateTests(Base, unittest.TestCase):
    def _callFUT(self, name, **kw):
        from repoze.bfg.chameleon_genshi import render_template
        return render_template(name, **kw)

    def test_it(self):
        minimal = self._getTemplatePath('minimal.genshi')
        result = self._callFUT(minimal)
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result,
                     '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>')

class RenderTemplateToResponseTests(Base, unittest.TestCase):
    def _callFUT(self, name, **kw):
        from repoze.bfg.chameleon_genshi import render_template_to_response
        return render_template_to_response(name, **kw)

    def test_it(self):
        minimal = self._getTemplatePath('minimal.genshi')
        result = self._callFUT(minimal)
        from webob import Response
        self.failUnless(isinstance(result, Response))
        self.assertEqual(result.app_iter,
                     ['<div xmlns="http://www.w3.org/1999/xhtml">\n</div>'])
        self.assertEqual(result.status, '200 OK')
        self.assertEqual(len(result.headerlist), 2)

    def test_iresponsefactory_override(self):
        from webob import Response
        class Response2(Response):
            pass
        from repoze.bfg.interfaces import IResponseFactory
        self._registerUtility(Response2, IResponseFactory)
        minimal = self._getTemplatePath('minimal.genshi')
        result = self._callFUT(minimal)
        self.failUnless(isinstance(result, Response2))

class GetRendererTests(Base, unittest.TestCase):
    def _callFUT(self, name):
        from repoze.bfg.chameleon_genshi import get_renderer
        return get_renderer(name)

    def test_nonabs_registered(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.chameleon_genshi import GenshiTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('minimal.genshi')
        utility = GenshiTemplateRenderer(minimal)
        self._registerUtility(utility, ITemplateRenderer, name=minimal)
        result = self._callFUT(minimal)
        self.assertEqual(result, utility)
        reg = get_current_registry()
        self.assertEqual(reg.queryUtility(ITemplateRenderer, minimal), utility)
        
    def test_nonabs_unregistered(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.chameleon_genshi import GenshiTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('minimal.genshi')
        reg = get_current_registry()
        self.assertEqual(reg.queryUtility(ITemplateRenderer, minimal), None)
        utility = GenshiTemplateRenderer(minimal)
        self._registerUtility(utility, ITemplateRenderer, name=minimal)
        result = self._callFUT(minimal)
        self.assertEqual(result, utility)
        self.assertEqual(reg.queryUtility(ITemplateRenderer, minimal), utility)

    def test_explicit_registration(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        class Dummy:
            template = object()
        utility = Dummy()
        self._registerUtility(utility, ITemplateRenderer, name='foo')
        result = self._callFUT('foo')
        self.failUnless(result is utility)

class GetTemplateTests(Base, unittest.TestCase):
    def _callFUT(self, name):
        from repoze.bfg.chameleon_genshi import get_template
        return get_template(name)

    def test_nonabs_registered(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.chameleon_genshi import GenshiTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('minimal.genshi')
        utility = GenshiTemplateRenderer(minimal)
        self._registerUtility(utility, ITemplateRenderer, name=minimal)
        result = self._callFUT(minimal)
        self.assertEqual(result.filename, minimal)
        reg = get_current_registry()
        self.assertEqual(reg.queryUtility(ITemplateRenderer, minimal), utility)
        
    def test_nonabs_unregistered(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.chameleon_genshi import GenshiTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('minimal.genshi')
        reg = get_current_registry()
        self.assertEqual(reg.queryUtility(ITemplateRenderer, minimal), None)
        utility = GenshiTemplateRenderer(minimal)
        self._registerUtility(utility, ITemplateRenderer, name=minimal)
        result = self._callFUT(minimal)
        self.assertEqual(result.filename, minimal)
        self.assertEqual(reg.queryUtility(ITemplateRenderer, minimal), utility)

    def test_explicit_registration(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        class Dummy:
            template = object()
            def implementation(self):
                return self.template
        utility = Dummy()
        self._registerUtility(utility, ITemplateRenderer, name='foo')
        result = self._callFUT('foo')
        self.failUnless(result is utility.template)
        
        
class Test_resolve_resource_spec(unittest.TestCase):
    def _callFUT(self, spec, package_name='__main__'):
        from repoze.bfg.chameleon_genshi import resolve_resource_spec
        return resolve_resource_spec(spec, package_name)

    def test_abspath(self):
        import os
        here = os.path.dirname(__file__)
        path = os.path.abspath(here)
        package_name, filename = self._callFUT(path, 'apackage')
        self.assertEqual(filename, path)
        self.assertEqual(package_name, None)

    def test_rel_spec(self):
        pkg = 'repoze.bfg.chameleon_genshi.tests'
        path = 'test_resource.py'
        package_name, filename = self._callFUT(path, pkg)
        self.assertEqual(package_name, 'repoze.bfg.chameleon_genshi.tests')
        self.assertEqual(filename, 'test_resource.py')
        
    def test_abs_spec(self):
        pkg = 'repoze.bfg.chameleon_genshi.tests'
        path = 'repoze.bfg.chameleon_genshi.nottests:test_resource.py'
        package_name, filename = self._callFUT(path, pkg)
        self.assertEqual(package_name, 'repoze.bfg.chameleon_genshi.nottests')
        self.assertEqual(filename, 'test_resource.py')

    def test_package_name_is_None(self):
        pkg = None
        path = 'test_resource.py'
        package_name, filename = self._callFUT(path, pkg)
        self.assertEqual(package_name, None)
        self.assertEqual(filename, 'test_resource.py')
        
class Test_abspath_from_resource_spec(unittest.TestCase):
    def _callFUT(self, spec, pname='__main__'):
        from repoze.bfg.chameleon_genshi import abspath_from_resource_spec
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
        result = self._callFUT('abc', 'repoze.bfg.chameleon_genshi.tests')
        self.assertEqual(result, os.path.join(path, 'abc'))

class TestXIncludes(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.chameleon_genshi import XIncludes
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
        result = xi.get('repoze.bfg.chameleon_genshi.tests:abc',
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
