import re
from decimal import Decimal
import datetime
import os

from tech.ironsheep.webdriver.command import Command

_PROTECTED_TYPES = (type(None), int, float, Decimal, datetime.datetime, datetime.date, datetime.time)
class Utils():

    # the last Loaded Path by file browser
    last_loaded_path = None

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

    @staticmethod
    def check_file_on_disk(s):
        """
        Return true if file exists
        Return false if not
        """
        s = Utils.force_text(s).strip().replace(' ', '_')
        s = re.sub(r'(?u)[^-\w.\\:]', '', s)
        
        if os.path.isfile(s):
            #print "File Found on Disk"
            return s
        else:
            #print "File Not Found."
            return ''

    @staticmethod
    def filter_device_id(val):
        """
        """
        val = Utils.force_text(val).strip().replace(' ', '')
        val = re.sub(r'(?u)[^\w+]', '', val)
        return val
        #'^\w+$'

    @staticmethod
    def get_path_relative_to_app(path, filename):
        return Utils.get_path_relative_to_path(path, Command.appDir, filename)

    @staticmethod
    def get_path_relative_to_path(path1, path2, filename):
        if path2 is None:
            return Utils.get_path_relative_to_app(path1, filename)

        rel_path = os.path.relpath(path1, path2)
        if rel_path == ".":
            filePath = Utils.get_filename_from_path(filename[0])
        else:
            filePath = rel_path + "\\" + Utils.get_filename_from_path(filename[0])

        if filePath == "":
            filePath = "."

        return rel_path, filePath



    @staticmethod
    def get_filename_from_path(path):
        try:
            filename = path[path.rindex('\\')+1:]
        except Exception as ex:
            filename = path

        return filename

    @staticmethod
    def get_absolute_path(path):
        return Command.appDir + "\\" + path

    @staticmethod
    def set_last_loaded_path(path):
        Utils.last_loaded_path = Utils.get_absolute_path(path)

    @staticmethod
    def get_last_loaded_path():
        return Utils.last_loaded_path
