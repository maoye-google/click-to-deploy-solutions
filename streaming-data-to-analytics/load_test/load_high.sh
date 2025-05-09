# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e

export GCP_TOKEN=$(gcloud auth print-identity-token)
export CLOUD_RUN_URL=$(gcloud run services describe ingest-api --region=us-east1 --format='value(status.url)')
export WAIT_TIME_INTERVAL=1

locust -f locustfile.py --headless -u 100 -r 10 \
    --run-time 20m \
    -H $CLOUD_RUN_URL
