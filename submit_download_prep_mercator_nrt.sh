#!/bin/bash -l
#SBATCH --partition=all      # Using normal partition
#SBATCH --container=el9hw
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --chdir=/ourdisk/hpc/ai2es/twu27/srcdata/Mercator_hourly
#SBATCH --output=./archives/merc_%J.out
#SBATCH --error=./archives/merc_%J.err
#SBATCH --time=1:00:00
#SBATCH --job-name=MercNRT

# Load conda environment
module purge
module load netCDF-C++4/4.3.1-iimpi-2025b
source /home/twu27/.bashrc
source /home/twu27/miniconda3/bin/activate
conda activate copernicusmarine2

run_date=$(date +%F)
start_date=$(date -d '-7 day' +%F)
end_date=$(date -d '+9 day' +%F)
mercator_file="/ourdisk/hpc/ai2es/twu27/srcdata/Mercator_hourly/archives/Mercator_${run_date}_zos_uovo.nc"

# download hourly mercator from CMEMS
copernicusmarine subset \
	--dataset-id cmems_mod_glo_phy_anfc_0.083deg_PT1H-m \
	--output-filename "${mercator_file}" \
	--variable zos --variable uo --variable vo \
	--start-datetime "${start_date}T00:00:00" --end-datetime "${end_date}T23:00:00" \
	--minimum-longitude -98 --maximum-longitude -74 \
	--minimum-latitude 17 --maximum-latitude 31 \
	--minimum-depth 0.49402499198913574 --maximum-depth 0.49402499198913574 \
	--coordinates-selection-method strict-inside \
	--disable-progress-bar --log-level ERROR

# Create Mercator_IC.nc and run the 6-hourly average in this job.

hostname
python mercator_6hourly_avg.py "${mercator_file}" Mercator_IC.nc
echo "6-hourly average completed."

echo "Download and average done!"
