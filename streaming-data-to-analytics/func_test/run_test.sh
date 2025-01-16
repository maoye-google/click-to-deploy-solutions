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

# export SA_NAME="ingest-api@streaming-events-demo-3-447707.iam.gserviceaccount.com"

export SA_NAME="external-cloud-run-user@streaming-events-demo-3-447707.iam.gserviceaccount.com"
export GOOGLE_APPLICATION_CREDENTIALS="./external_client_key.json"
# export CLOUD_RUN_ENDPOINT="https://ingest-api-978187934406.us-east1.run.app"
export CLOUD_RUN_ENDPOINT=$(gcloud run services describe ingest-api --region=us-east1 --format='value(status.url)')

python main.py