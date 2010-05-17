repoze.bfg.chameleon_genshi
===========================

Bindings for Chameleon Genshi-style templating support under
`repoze.bfg <http://bfg.repoze.org/>`_.  See the `Chameleon website
<http://chameleon.repoze.org>`_ for ``chameleon.genshi`` templating
language details.  This package module lacks its own documentation,
but the API for use under BFG is identical to the one used for
chameleon.zpt templates as documented in the "Templating" chapter of
the `BFG docs <http://docs.repoze.org/bfg>`_.  Only the templating
language itself and import locations differ.

An example::

  from repoze.bfg.chameleon_genshi import render_template_to_response
  render_template_to_response('relative/path/to/template')

``relative/path/to/template`` is relative to the package directory in
which the above code is defined.

See also the ``render_template`` and ``render_template_to_iterable``
APIs exposed by the ``repoze.bfg.chameleon_genshi`` package, which
serve the same purpose as their brethren in
``repoze.bfg.chameleon_zpt``.

Genshi templates can also be used as a BFG "renderer" when you use
``repoze.bfg.chameleon_genshi``.  In the ``run.py`` of your BFG
application, in the function called at startup, which uses a
``repoze.bfg.configuration.Configurator`` as ``config``::

  from repoze.bfg.chameleon_genshi import renderer_factory
  config.add_renderer('.genshi', renderer_factory)

Once you've registered ``.genshi`` as a renderer (it doesn't need to
literally be ``.genshi``, that's just what we registered the renderer
above as) , in a view configuration, you can do the following::

  @bfg_view(renderer='templates/foo.genshi')
  def someview(request):
      ....
