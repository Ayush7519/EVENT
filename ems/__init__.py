# this is for the celery.

from .celery import app as celery_app

__all__ = ("celery_app",)
