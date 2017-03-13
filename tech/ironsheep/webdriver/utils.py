import re
from decimal import Decimal
import datetime

_PROTECTED_TYPES = (type(None), int, float, Decimal, datetime.datetime, datetime.date, datetime.time)
class Utils():

    @staticmethod
    def force_text(s, encoding='utf-8', strings_only=False, errors='strict'):
        """
        Code taken from django: https://github.com/django/django/blob/master/django/utils/encoding.py
        Similar to smart_text, except that lazy instances are resolved to
        strings, rather than kept as lazy objects.
        If strings_only is True, don't convert (some) non-string-like objects.
        """
        # Handle the common case first for performance reasons.
        if issubclass(type(s), str):
            return s
        if strings_only and isinstance(s, _PROTECTED_TYPES):
            return s
        try:
            if isinstance(s, bytes):
                s = str(s, encoding, errors)
            else:
                s = str(s)
        except UnicodeDecodeError:
            pass
        return s

    @staticmethod
    def get_valid_filename(s):
        """
        Return the given string converted to a string that can be used for a clean
        filename. Remove leading and trailing spaces; convert other spaces to
        underscores; and remove anything that is not an alphanumeric, dash,
        underscore, or dot.
        """
        s = Utils.force_text(s).strip().replace(' ', '_')
        return re.sub(r'(?u)[^-\w.]', '', s)
