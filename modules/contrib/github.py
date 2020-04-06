# -*- coding: UTF-8 -*-

"""Displays the unread GitHub notifications for a GitHub user

Requires the following library:
    * requests

Parameters:
    * github.token: GitHub user access token, the token needs to have the 'notifications' scope.
"""

import core.module
import core.input

import requests


class Module(core.module.Module):
    @core.decorators.every(minutes=5)
    def __init__(self, config):
        super().__init__(config, core.widget.Widget(self.output))

        self.__count = 0

        self.__apikey = self.parameter('token')

        self.__requests = requests.Session()
        self.__requests.headers.update({"Authorization":"token {}".format(self.__apikey)})

        core.input.register(self, button=core.input.LEFT_MOUSE, cmd="x-www-browser https://github.com/notifications")
        core.input.register(self, button=core.input.RIGHT_MOUSE, cmd=self.update)

    def output(self, widget):
        return str(self.__count)

    def update(self):
        try:
            self.__count = 0
            url = "https://api.github.com/notifications"
            while True:
                notifications = self.__requests.get(url)
                self.__count += len(list(filter(lambda notification: notification['unread'], notifications.json())))
                next_link = notifications.links.get('next')
                if next_link is not None:
                    url = next_link.get('url')
                else:
                    break
        except Exception:
            self.__count = "n/a"
