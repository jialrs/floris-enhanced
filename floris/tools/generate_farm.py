import pandas as pd
from geopy import distance

DATA_FILE = r"f:\Notebook\floris-enhanced\examples\uswtdb_v3_0_1_20200514.csv"

def generate_farm(project_name: str):
    df = pd.read_csv(DATA_FILE)
    proj_turbine = df[df['p_name'] == project_name]
    x_series = proj_turbine['xlong'].tolist()
    y_series = proj_turbine['ylat'].tolist()
    #turbine_loc_list = zip(x_series, y_series)
    origin_loc = [min(x_series), min(y_series)]
    turbine_xloc_list = []
    turbine_yloc_list = []
    for x, y in zip (x_series, y_series):
        rel_x = distance.great_circle((y,x), (y, origin_loc[0])).m
        rel_y = distance.great_circle((y,x), (origin_loc[1],x)).m
        turbine_xloc_list.append(rel_x)
        turbine_yloc_list.append(rel_y)
        
    return turbine_xloc_list, turbine_yloc_list
    
    
if __name__ == "__main__":
     print(generate_farm("Alta I"))
