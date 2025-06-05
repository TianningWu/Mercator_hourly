#!/bin/bash -l
#
#SBATCH --partition=ai2es
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=1:00:00
#SBATCH --mem=64G
#SBATCH --output=./archives/avg_%J.out
#SBATCH --error=./archives/avg_%J.err
#SBATCH --job-name=AvgMerc

#  source my python env
source /home/twu27/.bashrc
source /home/twu27/python3/env/oceannet/bin/activate
module load Python/3.10.8-GCCcore-12.2.0
hostname

python mercator_6hourly_avg.py 