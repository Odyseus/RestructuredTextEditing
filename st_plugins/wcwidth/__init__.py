"""wcwidth module, https://github.com/jquast/wcwidth."""
from .wcwidth import wcswidth  # noqa
from .wcwidth import wcwidth

__all__ = ('wcwidth', 'wcswidth',)
