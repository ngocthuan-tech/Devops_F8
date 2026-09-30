Dựng 1 image cho 1 backend chạy môi trương production
- python3.14
- cài đăt thư viện poetry
- cài fastapi với poetry
- viết 1 api helloworld
===============================================================
BƯỚC LÀM
1. Chạy container `python:3.14-slim`, cài Poetry, dùng
   `poetry init` + `poetry add fastapi "uvicorn[standard]"`
   → sinh ra `pyproject.toml` và `poetry.lock`
2. Viết API hello world trong `app/main.py`
3. Viết Dockerfile production:
   - Multi-stage build (builder cài thư viện, runtime chỉ copy `.venv` + code)
   - Chạy bằng user thường `appuser`, không dùng root
   - Có HEALTHCHECK, uvicorn chạy 2 workers
4. Build & chạy:
```
   docker build -t hello-api:1.0 .
   docker run -d -p 8000:8000 --name hello-api hello-api:1.0
   curl http://localhost:8000
```



