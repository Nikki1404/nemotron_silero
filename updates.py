re_nikitav@EC03-E01-AICOE1:~$ sudo su
(base) root@EC03-E01-AICOE1:/home/CORP/re_nikitav# conda deactivate
root@EC03-E01-AICOE1:/home/CORP/re_nikitav# export AWS_ACCESS_KEY_ID="xxxxxx"
export AWS_SECRET_ACCESS_KEY="xxxxxx"
export AWS_SESSION_TOKEN="xxxxxxx"
root@EC03-E01-AICOE1:/home/CORP/re_nikitav# aws s3 ls s3://cx-speech

SSL validation failed for https://cx-speech.s3.us-east-1.amazonaws.com/?list-type=2&prefix=&delimiter=%2F&encoding-type=url [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate in certificate chain (_ssl.c:1032)
