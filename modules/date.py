# pylint: disable=C0111,R0903

'''Displays the current date and time.

Parameters:
    * date.format: strftime()-compatible formatting string
    * date.locale: locale to use rather than the system default
'''

from .datetime import Module

class Module(Module):
    def __init__(self, config):
        super().__init__(config)

    def default_format(self):
        return '%x'

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4