gcloud builds submit --tag gcr.io/xenon-crossbar-336406/hello --project=xenon-crossbar-336406

gcloud run deploy --image gcr.io/xenon-crossbar-336406/hello --platform managed --project=xenon-crossbar-336406 --allow-unauthenticated