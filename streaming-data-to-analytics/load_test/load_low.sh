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
export CLOUD_RUN_URL=https://ingest-api-378528575678.us-east1.run.app
export WAIT_TIME_INTERVAL=1

locust -f locustfile.py --headless -u 1 -r 1 \
    --run-time 5m \
    -H $CLOUD_RUN_URL