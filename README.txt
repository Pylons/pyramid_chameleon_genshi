repoze.bfg.chameleon_genshi
===========================

Bindings for Chameleon Genshi-style templating support under
`repoze.bfg <http://bfg.repoze.org/>`_.  See the `Chameleon website
<http://chameleon.repoze.org>`_ for ``chameleon.genshi`` templating
language details.  This package module lacks its own documentation,
but the API for use under BFG is identical to the one used for
chameleon.zpt templates as documented in the "Templating" chapter of
the `BFG docs <http://bfg.repoze.org/documentation>`_.  Only the
templating language itself and import locations differ.

An example::

  from repoze.bfg.chameleon_genshi import render_template_to_response
  render_template_to_response('relative/path/to/template')

``relative/path/to/template`` is relative to the package directory in
which the above code is defined.

See also the ``render_template`` and ``render_template_to_iterable``
APIs exposed by the ``repoze.bfg.chameleon_genshi`` package, which
serve the same purpose as their brethren in
``repoze.bfg.chameleon_zpt``.


