#!/bin/bash
#SBATCH -N 1
#SBATCH --mem=4G
#SBATCH --job-name=kdp-sail
#SBATCH --account=ATM124
#SBATCH --time=20:00:00 
#SBATCH --mail-user=braut@anl.gov
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH -p batch_all

cd /ccsopen/home/braut/pynb/kdp-computation
module load python
source activate /ccsopen/home/braut/analysis-env2
/ccsopen/home/braut/analysis-env2/bin/python ./kdp-lp.py --glob '/gpfs/wolf/atm124/proj-shared/gucxprecipradarcmacS2.c1/ppi/202208/*.nc' --out '/gpfs/wolf/atm124/proj-shared/gucxprecipradarcmacS2.c1-KDP/202208/'
