kubectl edit deployment/asr-realtime-custom-vad -n cx-speech 
# Please edit the object below. Lines beginning with a '#' will be ignored,
# and an empty file will abort the edit. If an error occurs while saving this file will be
# reopened with the relevant failures.
#
apiVersion: apps/v1
kind: Deployment
metadata:
  annotations:
    deployment.kubernetes.io/revision: "24"
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"name":"asr-realtime-custom-vad","namespace":"cx-speech"},"spec":{"replicas":1,"selector":{"matchLabels":{"app":"asr-realtime-custom-vad"}},"template":{"metadata":{"labels":{"app":"asr-realtime-custom-vad"},"name":"asr-realtime-custom-vad-pod"},"spec":{"affinity":{"nodeAffinity":{"requiredDuringSchedulingIgnoredDuringExecution":{"nodeSelectorTerms":[{"matchExpressions":[{"key":"eks.amazonaws.com/nodegroup","operator":"In","values":["gpu-dev-k8"]}]}]}}},"containers":[{"env":[{"name":"gpus","value":"all"}],"image":"058264113403.dkr.ecr.us-east-1.amazonaws.com/cx-speech/asr-realtime-custom-vad:0.0.1","imagePullPolicy":"Always","name":"asr-realtime-custom-vad-container","ports":[{"containerPort":8002}]}],"tolerations":[{"effect":"NoSchedule","key":"gpu","operator":"Equal","value":"true"}]}}}}
  creationTimestamp: "2026-02-06T11:42:12Z"
  generation: 71
  name: asr-realtime-custom-vad
  namespace: cx-speech
  resourceVersion: "200078110"
  uid: ac212681-5306-4e75-b620-b54d9b012054
spec:
  progressDeadlineSeconds: 600
  replicas: 1
  revisionHistoryLimit: 10
  selector:
    matchLabels:
      app: asr-realtime-custom-vad
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
  template:
    metadata:
      annotations:
        kubectl.kubernetes.io/restartedAt: "2026-02-06T11:51:40Z"
      creationTimestamp: null
      labels:
        app: asr-realtime-custom-vad
      name: asr-realtime-custom-vad-pod
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
                                                                                                                                                          1,1           Top

