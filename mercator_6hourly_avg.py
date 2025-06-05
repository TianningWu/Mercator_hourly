from datetime import datetime
from netCDF4 import Dataset

# Open your dataset
today_str = datetime.today().strftime('%Y-%m-%d')
infilename = f'./archives/Mercator_{today_str}_zos_uovo.nc'
outfilename = f'./Mercator_IC.nc'
ds_in = Dataset(infilename,'r')
ds_out = Dataset(outfilename,'a')

# Define the rolling window size (24 hours) and stride (6 hours)
window_size = 24  # hours
step = 6          # hours

# Loop over time using 6-hour steps
nrec=0
for start in range(0, len(ds_in.variables['time'][:]) - window_size + 1, step):
    print(ds_in.variables['time'][start])
    
    ds_out.variables['time'][nrec] = ds_in.variables['time'][start]
    ds_out.variables['zos'][nrec,:,:,:] = ds_in.variables['zos'][start:start+window_size,:,:,:].mean(0)
    ds_out.variables['uo'][nrec,:,:,:] = ds_in.variables['uo'][:][start:start+window_size,:,:,:].mean(0)
    ds_out.variables['vo'][nrec,:,:,:] = ds_in.variables['vo'][:][start:start+window_size,:,:,:].mean(0)

    nrec+=1

ds_in.close()
ds_out.close()