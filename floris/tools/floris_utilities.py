# Copyright 2019 NREL

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import numpy as np
from floris.simulation import Floris
from .flow_field import FlowField
from ..utilities import Vec3


class FlorisInterface():
    """
    The interface from FLORIS to the wfc tools
    """

    def __init__(self, input_file):
        self.input_file = input_file
        self.floris = Floris(input_file=input_file)

    def run_floris(self):
        """
        This method runs the FLORIS model with the current model parameters.
        """
        self.floris.calculate_wake()

    def get_flow_field(self, resolution=None, grid_spacing=10):
        if resolution is None:
            if not self.floris.farm.flow_field.wake.velocity_model.requires_resolution:
                print('Assuming grid with spacing %d' % grid_spacing)
                xmin, xmax, ymin, ymax, zmin, zmax = self.floris.farm.flow_field.domain_bounds
                resolution = Vec3(
                    1 + (xmax - xmin) / grid_spacing,
                    1 + (ymax - ymin) / grid_spacing,
                    1 + (zmax - zmin) / grid_spacing
                )
            else:
                print('Assuming model resolution')
                resolution = self.floris.farm.flow_field.wake.velocity_model.model_grid_resolution

        flow_field = self.floris.farm.flow_field
        if flow_field.wake.velocity_model.requires_resolution and \
            flow_field.wake.velocity_model.model_grid_resolution != resolution:
            print("WARNING: The current wake velocity model contains a required grid resolution;")
            print("    The Resolution given to FlorisInterface.get_flow_field is ignored.")
            resolution = flow_field.wake.velocity_model.model_grid_resolution
        flow_field.calculate_wake(with_resolution=resolution)

        order = "f"
        x = flow_field.x.flatten(order=order)
        y = flow_field.y.flatten(order=order)
        z = flow_field.z.flatten(order=order)

        u = flow_field.u.flatten(order=order)
        v = flow_field.v.flatten(order=order)
        w = flow_field.w.flatten(order=order)

        # Determine spacing, dimensions and origin
        unique_x = np.sort(np.unique(x))
        unique_y = np.sort(np.unique(y))
        unique_z = np.sort(np.unique(z))
        spacing = Vec3(
            unique_x[1] - unique_x[0],
            unique_y[1] - unique_y[0],
            unique_z[1] - unique_z[0]
        )
        dimensions = Vec3(len(unique_x), len(unique_y), len(unique_z))
        origin = Vec3(0.0, 0.0, 0.0)
        return FlowField(x, y, z, u, v, w, spacing=spacing, dimensions=dimensions, origin=origin)

    def get_yaw_angles(self):
        yaw_angles = [turbine.yaw_angle for turbine in self.floris.farm.turbine_map.turbines]
        return yaw_angles

    def get_farm_power(self):
        turb_powers = [turbine.power for turbine in self.floris.farm.turbines]
        return np.sum(turb_powers)

    def get_turbine_power(self):
        turb_powers = [turbine.power for turbine in self.floris.farm.turbines]
        return turb_powers

        # calculate the power under different yaw angles
    def get_power_with_yaw_angles(self,yaw_angles):    
        
        # assign yaw angles to turbines and calculate wake
        self.floris.farm.set_yaw_angles(yaw_angles, calculate_wake=True)
        
        power = -1 * np.sum([turbine.power for turbine in self.floris.farm.turbines]) 

        return power/(10**3)
