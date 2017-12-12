"""
Copyright 2017 NREL

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""

from .BaseObject import BaseObject
import numpy as np


class WakeDeflection(BaseObject):

    def __init__(self, type_string, parameter_dictionary):
        super().__init__()
        self.type_string = type_string

        type_map = {
            "jimenez": self._jimenez
        }
        self.function = type_map.get(self.type_string, None)

        # loop through all the properties defined in the parameter dict and
        # store as attributes of the WakeVelocity object
        for key, value in parameter_dictionary.items():
            setattr(self, key, value)

        self.kd = float(self.jimenez["kd"])
        self.ad = float(self.jimenez["ad"])
        self.bd = float(self.jimenez["bd"])

    def _jimenez(self, x_locations, turbine, coord):
        # this function defines the angle at which the wake deflects in relation to the yaw of the turbine
        # this is coded as defined in the Jimenez et. al. paper

        # angle of deflection
        xi_init = (1. / 2.) * np.cos(turbine.yaw_angle) * \
            np.sin(turbine.yaw_angle) * turbine.Ct
        # xi = xi_init / (1 + 2 * self.kd * x_locations / turbine.rotor_diameter)**2
        
        x_locations = x_locations - coord.x

        # yaw displacement
        yYaw_init = ( xi_init
            * ( 15 * (2 * self.kd * x_locations / turbine.rotor_diameter + 1)**4. + xi_init**2. )
            / ((30 * self.kd / turbine.rotor_diameter) * (2 * self.kd * x_locations / turbine.rotor_diameter + 1)**5.)) \
            - (xi_init * turbine.rotor_diameter * (15 + xi_init**2.) / (30 * self.kd))

        # corrected yaw displacement with lateral offset
        yYaw = yYaw_init + self.ad + self.bd * x_locations

        return yYaw
