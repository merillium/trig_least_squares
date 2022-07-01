#!/bin/bash
gcloud builds submit --tag gcr.io/xenon-crossbar-336406/dash-apps --project=xenon-crossbar-336406
gcloud run deploy --image gcr.io/xenon-crossbar-336406/dash-apps --platform managed --project=xenon-crossbar-336406 --allow-unauthenticated