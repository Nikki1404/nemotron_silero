(base) root@EC03-E01-AICOE1:/home/CORP/re_nikitav# kubectl get nodes -o=custom-columns=NAME:.metadata.name,GPUs:.status.allocatable.nvidia\.com/gpu
NAME                            GPUs
ip-10-90-114-104.ec2.internal   <none>
ip-10-90-114-153.ec2.internal   <none>
ip-10-90-114-166.ec2.internal   <none>
ip-10-90-114-186.ec2.internal   <none>
ip-10-90-114-72.ec2.internal    <none>
ip-10-90-114-87.ec2.internal    <none>
ip-10-90-126-146.ec2.internal   <none>
ip-10-90-126-19.ec2.internal    <none>
