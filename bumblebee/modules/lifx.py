# pylint: disable=C0111,R0903

"""Changes the brightness of a LIFX light/group/location/scene

Requires the following library:
    * requests

Parameters:
    * lifx.token: LIFX access token. Can be created here: https://cloud.lifx.com/settings
    * lifx.selector: Light selector, see https://api.developer.lifx.com/docs/selectors for more infos about selectors.
    * lifx.duration: How long in seconds you want the power action to take. (defaults to 0)
    * lifx.increment: Change increment. (defaults to 0.1)
"""

import json
import functools
import bumblebee.engine

try:
    import requests
except ImportError:
    pass

class Module(bumblebee.engine.Module):
    def __init__(self, engine, config):
        super(Module, self).__init__(engine, config,
            bumblebee.output.Widget(full_text=self.lifx)
        )
        # FIXME: check this
        self.interval_factor(60)
        self.interval(5)

        duration = float(self.parameter("duration", "0"))
        increment = float(self.parameter("increment", "0.1"))

        inc_brightness = functools.partial(self.set_delta, state={'duration': duration, 'brightness': increment})
        dec_brightness = functools.partial(self.set_delta, state={'duration': duration, 'brightness': -increment})
        engine.input.register_callback(self, button=bumblebee.input.WHEEL_UP, cmd=inc_brightness)
        engine.input.register_callback(self, button=bumblebee.input.WHEEL_DOWN, cmd=dec_brightness)
        engine.input.register_callback(self, button=bumblebee.input.LEFT_MOUSE, cmd=self.toggle)
        engine.input.register_callback(self, button=bumblebee.input.RIGHT_MOUSE, cmd=self.update)

        self._requests = requests.Session()
        self._requests.headers.update({"Authorization":"Bearer {}".format(self.parameter("token", ""))})

        self._selector = self.parameter("selector", "")

        self._text = 'n/a'

    def lifx(self, _):
        return self._text

    def update(self, _):
        response = self._requests.get("https://api.lifx.com/v1/lights/{}".format(self._selector))
        if response.ok:
          states = response.json()
          if len(states) == 1:
              state = states[0]
              # assuming that an unconnected light was turned off by the good old switch
              if state.get('connected') is False or state.get('power') == 'off':
                  self._text = "off"
              else:
                  self._text = "{:.0%}".format(state.get('brightness'))
        else:
            self._text = 'n/a'

    def toggle(self, _):
        self._requests.post("https://api.lifx.com/v1/lights/{}/toggle".format(self._selector))
        self.update(None)

    def set_delta(self, _, state):
        self._requests.post("https://api.lifx.com/v1/lights/{}/state/delta".format(self._selector), data=json.dumps(state))
        self.update(None)
