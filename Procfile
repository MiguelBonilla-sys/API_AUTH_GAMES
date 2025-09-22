web: gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --timeout 120 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100
