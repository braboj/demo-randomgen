"""Flask blueprints for the RandomGen service.

The HTTP routes are grouped by audience: :mod:`~randomgen.blueprints.web` holds
the unversioned, browser- and ops-facing routes, and
:mod:`~randomgen.blueprints.api` builds one versioned API blueprint per entry in
the version registry. The application factory in :mod:`randomgen.app` registers
them all.
"""
