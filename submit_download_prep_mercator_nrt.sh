#!/bin/bash -l
#SBATCH --partition=ai2es      # Using normal partition
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --output=./archives/down_%J.out
#SBATCH --error=./archives/down_%J.err
#SBATCH --time=1:00:00      # 2 days (maximum time limit for normal partition)
#SBATCH --job-name=DownMerc

# Load conda environment
module purge
source /home/twu27/.bashrc
source /home/twu27/miniconda3/bin/activate
conda activate copernicusmarine
module load NCO/5.1.3-foss-2021a

# download hourly mercator from CMEMS
copernicusmarine subset \
	--dataset-id cmems_mod_glo_phy_anfc_0.083deg_PT1H-m \
	--output-filename ./archives/Mercator_$(date +%F)_zos_uovo.nc \
	--variable zos --variable uo --variable vo \
	--start-datetime $(date -d '-7 day' +%F)T00:00:00 --end-datetime $(date -d '+9 day' +%F)T23:00:00 \
	--minimum-longitude -98 --maximum-longitude -74 \
	--minimum-latitude 17 --maximum-latitude 31 \
	--minimum-depth 0.49402499198913574 --maximum-depth 0.49402499198913574 \
	--coordinates-selection-method strict-inside \
	--disable-progress-bar --log-level ERROR

# write invariants into Mercator_IC.nc, which will be the initial conditions for oceannet
rm Mercator_IC.nc
ncgen -4 -o Mercator_IC.nc ./archives/mercator.cdl
ncks -A -v depth,latitude,longitude ./archives/Mercator_$(date +%F)_zos_uovo.nc Mercator_IC.nc

# Submit avg
jid3=$(sbatch --parsable mercator_6hourly_avg.sh)
echo "Submitted daily average with Job ID $jid3"
sacct -j $jid3 --format=State --noheader | grep -q COMPLETED
while [ $? -ne 0 ]; do
    sleep 5
    sacct -j $jid3 --format=State --noheader | grep -q COMPLETED
done
echo "Daily average completed."

echo "Download and average done!"