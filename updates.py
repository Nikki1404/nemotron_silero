unset http_proxy
unset https_proxy
export the keys for AWS
kubectl scale deployment asr-realtime-custom-vad -n cx-speech --replicas=0
kubectl set image deployment/asr-realtime-custom-vad asr-realtime-custom-vad-container=058264113403.dkr.ecr.us-east-1.amazonaws.com/cx-speech/asr-realtime-custom-vad:0.0.19 -n cx-speech
kubectl scale deployment asr-realtime-custom-vad -n cx-speech --replicas=1
Test to see if it is working fine, and if it does not work then revert to the original version by running the following commands:
kubectl scale deployment asr-realtime-custom-vad -n cx-speech --replicas=0
kubectl set image deployment/asr-realtime-custom-vad asr-realtime-custom-vad-container=058264113403.dkr.ecr.us-east-1.amazonaws.com/cx-speech/asr-realtime-custom-vad:0.0.16 -n cx-speech
kubectl scale deployment asr-realtime-custom-vad -n cx-speech --replicas=1
