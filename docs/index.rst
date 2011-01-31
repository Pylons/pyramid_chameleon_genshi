pyramid_chameleon_genshi
========================

:mod:`pyramid_chameleon_genshi` provides bindings for Chameleon Genshi-style
templating support under `Pyramid <http://docs.pylonsproject.org/>`_.  See
the `Chameleon website <http://chameleon.repoze.org>`_ for
``chameleon.genshi`` templating language details.

Usage
-----

The API for use of ``pyramid_chameleon_genshi`` under Pyramid is identical to
the one used for `chameleon.zpt`` templates as documented in the "Templating"
chapter of the `Pyramid docs
<http://docs.pylonshq.com/pyramid/dev/narr/templates.html#chameleon-zpt-templates>`_.
Only the templating language itself (Genshi vs. ZPT).

An example::

  from pyramid.renderers import render_to_response

  return render_template_to_response(
                'mypackage:templates/template.genshi', {'a':1})

``mypackage:templates`` is a Pyramid *asset specification* that ends in
``.genshi`` which points at a Chameleon Genshi template.

Chameleon Genshi templates can be used as a Pyramid "renderer" like this when
you use ``pyramid_chameleon_genshi``.

The easiest way to allow for this is to use an ``include`` the startup code
if your application.  In the ``__init__.py`` of your Pyramid
application, in the ``main`` function called at startup (which uses a
``pyramid.configuration.Configurator`` as ``config``) add the following::

  config.include('pyramid_chameleon_genshi')

You can also drive this particular oxcart by hand (the below achieves the
same goal as the above ``include``)::

  from pyramid_chameleon_genshi import renderer_factory

  config.add_renderer('.genshi', renderer_factory)

Once this is done, you can use Genshi templates from within an ``add_view``
statement or from within a ``pyramid.views.view_config`` decorator.  For
example::

  @view_config(renderer='mypackage:templates/foo.genshi')
  def someview(request):
      ....

If you'd rather not use a ``.genshi`` extension for your ``chameleon.genshi``
templates, you can explicitly register a renderer using the ``add_renderer``
method of a "configurator"::

  from pyramid_chameleon_genshi import renderer_factory
  config.add_renderer('.cgenshi', renderer_factory)

Once you've registered ``.cgenshi`` as a renderer in a view configuration,
you can then do the following::

  @view_config(renderer='templates/foo.cgenshi')
  def someview(request):
      ....

Using With ZCML
~~~~~~~~~~~~~~~

If you use the ``pyramid_zcml`` package, instead of using
``config.add_renderer``, you can add this ZCML to your application's
``configure.zcml``::

  <include package="pyramid_chameleon_genshi"/>

Once your application has been set up to process this ZCML, your application
can point at ``chameleon.genshi`` templates that have the ``.genshi`` file.
For example::

   <view
     renderer="templates/foo.genshi"
     view=".views.someview"/>

Misc
----

By default, Chameleon's Genshi XIncludes support cannot resolve Pyramid
"asset specifications" (e.g. ``my_package:foo/bar.genshi``).  In order to
activate an XIncludes class that understands Pyramid asset specifications,
call the ``pyramid_chameleon_genshi.XIncludes.activate`` method before using
any templates (e.g., at process startup time)::

  from pyramid_chameleon_genshi import XIncludes
  XIncludes.activate()

This will replace the XIncludes helper class for all consumers of
Chameleon in the process.

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
