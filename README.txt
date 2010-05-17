repoze.bfg.chameleon_genshi
===========================

Bindings for Chameleon Genshi-style templating support under
`repoze.bfg <http://bfg.repoze.org/>`_.  See the `Chameleon website
<http://chameleon.repoze.org>`_ for ``chameleon.genshi`` templating
language details.

The API for use of ``repoze.bfg.chameleon_genshi`` under BFG is
identical to the one used for `chameleon.zpt`` templates as documented
in the "Templating" chapter of the `BFG docs
<http://docs.repoze.org/bfg/1.3/narr/templates.html#chameleon-zpt-templates>`_.
Only the templating language itself (Genshi vs. ZPT) and import
locations (r.b.chameleon_genshi vs. r.b.chameleon_zpt) differ.

An example::

  from repoze.bfg.chameleon_genshi import render_template_to_response
  render_template_to_response('relative/path/to/template')

``relative/path/to/template`` is relative to the package directory in
which the above code is defined.

See also the ``render_template`` and ``get_template`` APIs exposed by
the ``repoze.bfg.chameleon_genshi`` package, which serve the same
purpose as their brethren in ``repoze.bfg.chameleon_zpt``.

Genshi templates can also be used as a BFG "renderer" when you use
``repoze.bfg.chameleon_genshi``.  The easiest way to allow for this is
to use the following ZCML in your application's ``configure.zcml``::

  <include package="repoze.bfg.chameleon_genshi"/>

Once your application has been set up to process this ZCML, your
application can point at ``chameleon.genshi`` templates that have the
``.genshi`` file extension from within ``@bfg_view`` directives or
ZCML ``view`` directives in your application.  For example::

  @bfg_view(renderer='templates/foo.genshi')
  def someview(request):
      ....

Or::

   <view
     renderer="templates/foo.genshi"
     view=".views.someview"/>

If you'd rather not use a ``.genshi`` extension for your
``chameleon.genshi`` templates, or if you'd rather not use ZCML to do
registration, you can explicitly register a renderer using a different
extension.  In the ``run.py`` of your BFG application, in the function
called at startup, which uses a
``repoze.bfg.configuration.Configurator`` as ``config``::

  from repoze.bfg.chameleon_genshi import renderer_factory
  config.add_renderer('.cgenshi', renderer_factory)

Once you've registered ``.cgenshi`` as a renderer in a view
configuration, you can do the following::

  @bfg_view(renderer='templates/foo.cgenshi')
  def someview(request):
      ....
