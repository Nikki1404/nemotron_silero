(base) root@EC03-E01-AICOE1:/home/CORP/re_nikitav/cx-speech-tts-other-models/kokoro# gcloud auth login
Go to the following link in your browser, and complete the sign-in prompts:

    https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=32555940559.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Fsdk.cloud.google.com%2Fauthcode.html&scope=openid+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fappengine.admin+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fsqlservice.login+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcompute+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Faccounts.reauth&state=3xJ1GNHKVu3mLqRbyUa4EweFpf9b5h&prompt=consent&token_usage=remote&access_type=offline&code_challenge=Fet5nOQ4pgg69a3oG1iBN-JvxPs3e9J60EOX_suQraQ&code_challenge_method=S256

Once finished, enter the verification code provided in your browser: 4/0AfrIepBoFOC2oo-QC8T6P5zTfY-vmnDf7dVifscc7Ec0dFqm0RY-thm8XvtmiMjJy7bDdQ

You are now logged in as [re_nikitav@exlservice.com].
Your current project is [emr-dgt-autonomous-uctr1-snbx].  You can change this setting by running:
  $ gcloud config set project PROJECT_ID
(base) root@EC03-E01-AICOE1:/home/CORP/re_nikitav/cx-speech-tts-other-models/kokoro#  gcloud config set project emr-dgt-autonomous-uctr1-snbx
WARNING: Your active project does not match the quota project in your local Application Default Credentials file. This might result in unexpected quota issues.

To update your Application Default Credentials quota project, use the `gcloud auth application-default set-quota-project` command.
Updated property [core/project].
(base) root@EC03-E01-AICOE1:/home/CORP/re_nikitav/cx-speech-tts-other-models/kokoro#  gcloud auth configure-docker us-central1-docker.pkg.dev
WARNING: Your config file at [/root/.docker/config.json] contains these credential helper entries:

{
  "credHelpers": {
    "us-central1-docker.pkg.dev": "gcloud"
  }
}
Adding credentials for: us-central1-docker.pkg.dev
gcloud credential helpers already registered correctly.
(base) root@EC03-E01-AICOE1:/home/CORP/re_nikitav/cx-speech-tts-other-models/kokoro# ls
Dockerfile  README.md  client.py  main.py  output.mp3  requirements.txt  router.py
(base) root@EC03-E01-AICOE1:/home/CORP/re_nikitav/cx-speech-tts-other-models/kokoro# vi Dockerfile
(base) root@EC03-E01-AICOE1:/home/CORP/re_nikitav/cx-speech-tts-other-models/kokoro#  gcloud builds submit --tag us-central1-docker.pkg.dev/emr-dgt-autonomous-uctr1-snbx/cx-speech/kokoro_openai_tts:0.0.1
Creating temporary archive of 7 file(s) totalling 266.0 KiB before compression.
Uploading tarball of [.] to [gs://emr-dgt-autonomous-uctr1-snbx_cloudbuild/source/1772120479.771315-e4f12de12d0c41068040cc2d514eb816.tgz]
Created [https://cloudbuild.googleapis.com/v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/eaf0be4f-de4a-4eca-bcbb-83fff343e466].
Logs are available at [ https://console.cloud.google.com/cloud-build/builds/eaf0be4f-de4a-4eca-bcbb-83fff343e466?project=150916788856 ].
Waiting for build to complete. Polling interval: 1 second(s).
-------------------------------------------------------- REMOTE BUILD OUTPUT --------------------------------------------------------
starting build "eaf0be4f-de4a-4eca-bcbb-83fff343e466"

FETCHSOURCE
Fetching storage object: gs://emr-dgt-autonomous-uctr1-snbx_cloudbuild/source/1772120479.771315-e4f12de12d0c41068040cc2d514eb816.tgz#1772120519218338
Copying gs://emr-dgt-autonomous-uctr1-snbx_cloudbuild/source/1772120479.771315-e4f12de12d0c41068040cc2d514eb816.tgz#1772120519218338...
/ [1 files][190.5 KiB/190.5 KiB]
Operation completed over 1 objects/190.5 KiB.
BUILD
Already have image (with digest): gcr.io/cloud-builders/docker
Sending build context to Docker daemon  279.6kB
Error response from daemon: dockerfile parse error line 38: FROM requires either one or three arguments
ERROR
ERROR: build step 0 "gcr.io/cloud-builders/docker" failed: step exited with non-zero status: 1
-------------------------------------------------------------------------------------------------------------------------------------

BUILD FAILURE: Build step failure: build step 0 "gcr.io/cloud-builders/docker" failed: step exited with non-zero status: 1
ERROR: (gcloud.builds.submit) build eaf0be4f-de4a-4eca-bcbb-83fff343e466 completed with status "FAILURE"
