# Copyright 2020 NREL
 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
 
# See https://floris.readthedocs.io for documentation
 

import matplotlib.pyplot as plt
import floris.tools as wfct
import floris.tools.visualization as vis
import floris.tools.cut_plane as cp
from floris.tools.optimization.scipy.yaw_wind_rose \
	import YawOptimizationWindRose
import floris.tools.wind_rose as rose
import floris.tools.power_rose as pr
import numpy as np
import pandas as pd
import os

# Define wind farm coordinates and layout
wf_coordinate = [39.8283, -98.5795]

# set min and max yaw offsets for optimization
min_yaw = 0.0
max_yaw = 25.0

# Define minimum and maximum wind speed for optimizing power. 
# Below minimum wind speed, assumes power is zero.
# Above maximum_ws, assume optimal yaw offsets are 0 degrees
minimum_ws = 3.0
maximum_ws = 15.0

# Instantiate the FLORIS object
file_dir = os.path.dirname(os.path.abspath(__file__))
fi = wfct.floris_interface.FlorisInterface(
    os.path.join(file_dir, '../../../example_input.json')
)

# Set wind farm to N_row x N_row grid with constant spacing 
# (2 x 2 grid, 5 D spacing)
D = fi.floris.farm.turbines[0].rotor_diameter
N_row = 2
spc = 5
layout_x = []
layout_y = []
for i in range(N_row):
	for k in range(N_row):
		layout_x.append(i*spc*D)
		layout_y.append(k*spc*D)
N_turb = len(layout_x)

fi.reinitialize_flow_field(
	layout_array=(layout_x, layout_y),
	wind_direction=[270.0],
	wind_speed=[8.0]
)
fi.calculate_wake()

# ==============================================================================
print('Plotting the FLORIS flowfield...')
# ==============================================================================

# Initialize the horizontal cut
hor_plane = fi.get_hor_plane(
    height=fi.floris.farm.turbines[0].hub_height
)

# Plot and show
fig, ax = plt.subplots()
wfct.visualization.visualize_cut_plane(hor_plane, ax=ax)
ax.set_title('Baseline flow for U = 8 m/s, Wind Direction = 270$^\circ$')

# ==============================================================================
print('Importing wind rose data...')
# ==============================================================================

# Create wind rose object and import wind rose dataframe using WIND Toolkit
# HSDS API. Alternatively, load existing file with wind rose information.
calculate_new_wind_rose = False

wind_rose = rose.WindRose()

if calculate_new_wind_rose:

	wd_list = np.arange(0,360,5)
	ws_list = np.arange(0,26,1)

	df = wind_rose.import_from_wind_toolkit_hsds(
		wf_coordinate[0],
	    wf_coordinate[1],
	    ht = 100,
	    wd = wd_list,
	    ws = ws_list,
	    limit_month = None,
	    st_date = None,
	    en_date = None
	)

else:
	df = wind_rose.load(os.path.join(
		file_dir, '../windtoolkit_geo_center_us.p'
	))

# plot wind rose
wind_rose.plot_wind_rose()

# =============================================================================
print('Finding baseline and optimal yaw angles in FLORIS...')
# =============================================================================

# Instantiate the Optimization object
yaw_opt = YawOptimizationWindRose(
	fi,
	df.wd,
	df.ws,
	minimum_yaw_angle=min_yaw,
	maximum_yaw_angle=max_yaw,
	minimum_ws=minimum_ws,
	maximum_ws=maximum_ws
)

# Determine baseline power with and without wakes
df_base = yaw_opt.calc_baseline_power()

# Perform optimization
df_opt = yaw_opt.optimize()

# Initialize power rose
case_name = 'Example '+str(N_row)+' x '+str(N_row)+ ' Wind Farm'
power_rose = pr.PowerRose()
power_rose.make_power_rose_from_user_data(
	case_name,
	df,
	df_base['power_no_wake'],
	df_base['power_baseline'],
	df_opt['power_opt']
)

# Summarize using the power rose module
fig, axarr = plt.subplots(3, 1, sharex=True, figsize=(6.4, 6.5))
power_rose.plot_by_direction(axarr)
power_rose.report()

plt.show()
