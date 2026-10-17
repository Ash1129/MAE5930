"""Posit Connect entrypoint. Import path is app:app.

Local use stays `python -m webapp.app`. Connect imports this module and does not
call app.run.
"""

from webapp.app import app

__all__ = ["app"]
