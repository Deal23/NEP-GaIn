#!/bin/bash
#SBATCH -J cp2k  
#SBATCH -p normal
#SBATCH -N 2   
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=30            
#SBATCH -t 24:00:00  
#SBATCH -o cp2k.o%j  
#SBATCH -e cp2k.e%j  

module load apps/cp2k/2024.1-hpcx-2.13.1-gcc-9.3.1-wangxh

echo "JOB began at $(date)"
echo "Total MPI tasks: $SLURM_NTASKS"
echo "Tasks per node: $SLURM_NTASKS_PER_NODE"
echo "CPUs per task: $SLURM_CPUS_PER_TASK"
gres_line=$(grep -oP '^#SBATCH\s+--gres=dcu:\K\d+' "$0")
node_line=$(grep -oP '^#SBATCH\s+-N\s+\K\d+' "$0") 
echo "DCU per node : $gres_line"
echo "Total DCUs : $(( gres_line * node_line ))"

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OMP_PROC_BIND=true
export OMP_PLACES=cores

mpirun --oversubscribe -np $SLURM_NTASKS cp2k.psmp -i input.inp -o cp2k.log

echo "JOB completed at $(date)"
