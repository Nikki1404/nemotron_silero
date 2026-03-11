kubectl get nodes -o=custom-columns=NAME:.metadata.name,GPUs:.status.allocatable.nvidia\.com/gpu
