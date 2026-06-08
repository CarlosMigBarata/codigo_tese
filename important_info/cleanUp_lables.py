
import pandas as pd
df = pd.read_csv('/home/sofia/Desktop/codigo_tese/codigo_tese/important_info/results/full_run/labels.csv', index_col=0)
cols = ['id','Residential','Commercial','Industrial','Cafe','Hotel','Restaurant','Store','MiscCommercial','Suburban','MiscResidential','CountryHouse','ConstructionSite','MiscIndustrial','PowerPlant','WaterTreatment','Door','Window','Awning','Billboard','Porch','Sign','Table','TiledRoof','TiledRoofTop','TiledRoofBottom','VendingMachine','WallSign','Statue','Chimney','Pipe','Machine','Truck','Car']
df[cols].to_csv('/home/sofia/Desktop/codigo_tese/codigo_tese/important_info/all.csv')

