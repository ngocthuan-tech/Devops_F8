# Bài tập buổi 10-11 - Deploy API lên ECS và DB lên RDS

## Đề bài

- Viết 1 API nhỏ có kết nối DB
- Deploy API lên ECS và DB lên RDS, kết nối chúng với nhau
- Gửi link ECS (public IP) và kiến trúc dự án

---

## Link ECS

- Swagger: http://54.255.241.178:8000/docs
- Kiểm tra kết nối DB: http://54.255.241.178:8000/db

Video demo: https://youtu.be/OPoH4qvxM-E

Nếu lúc thầy vào link không được thì có thể task đã bị restart và đổi IP, minh chứng em để ở phần dưới.

---

## Kiến trúc
<img width="1400" height="830" alt="image" src="https://github.com/user-attachments/assets/413157ad-28d7-4f38-9d47-a89fe38d2c92" />



- Region: ap-southeast-1 (Singapore), chọn vì gần Việt Nam
- Dùng Default VPC có sẵn
- API viết bằng FastAPI, build thành Docker image rồi đẩy lên Docker Hub
- ECS Fargate kéo image về chạy trong public subnet, bật public IP, mở port 8000
- RDS PostgreSQL để Public access = No, ngoài Internet không vào thẳng được
- ECS và RDS nối với nhau bằng security group: rds-sg chỉ cho phép port 5432 từ ecs-sg
- Thông tin kết nối DB (host, user, password) truyền vào container bằng environment variables, không ghi trong code
- Log của container đẩy về CloudWatch Logs

### Thông số

| Thành phần | Cấu hình |
|---|---|
| Region | ap-southeast-1 (Singapore) |
| VPC | Default VPC |
| ECS | Fargate, cluster day10-cluster, 0.25 vCPU / 0.5 GB |
| Container | notes-api, port 8000 |
| RDS | PostgreSQL 18, db.t4g.micro, Single-AZ, 20 GB gp3 |
| ecs-sg | Inbound TCP 8000 từ 0.0.0.0/0 |
| rds-sg | Inbound PostgreSQL 5432 chỉ từ ecs-sg |

---

## API

| Method | Path | Chức năng |
|---|---|---|
| GET | / | Hello World |
| GET | /health | Health check |
| GET | /db | Kiểm tra kết nối DB, trả về version PostgreSQL |
| POST | /notes | Thêm ghi chú vào DB |
| GET | /notes | Lấy danh sách ghi chú |

Khi app khởi động sẽ tự tạo bảng `notes` nếu chưa có.

---

## Các bước làm

1. Viết API bằng FastAPI, kết nối PostgreSQL bằng thư viện psycopg, quản lý thư viện bằng Poetry
2. Test trên máy bằng Docker: chạy 1 container postgres và 1 container app chung network
3. Build image và đẩy lên Docker Hub
4. Tạo RDS PostgreSQL (db.t4g.micro, Single-AZ, Public access = No), security group rds-sg
5. Tạo ecs-sg mở port 8000, sửa rds-sg chỉ cho phép port 5432 từ ecs-sg
6. Tạo ECS cluster loại Fargate
7. Tạo task definition: image trên Docker Hub, port 8000, các biến môi trường DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
8. Chạy task trong public subnet, bật public IP, gắn ecs-sg
9. Vào link /db để kiểm tra kết nối DB, vào /docs để test thêm và xem dữ liệu

---

## Minh chứng

### RDS đang chạy
<img width="1363" height="231" alt="image" src="https://github.com/user-attachments/assets/c84f2536-2d09-41ff-8eeb-8f7685fce40c" />

### Security group
<img width="1468" height="399" alt="image" src="https://github.com/user-attachments/assets/6d3290c3-6c03-49ac-8521-4aa69ee26069" />

ecs-sg mở port 8000:
<img width="1353" height="490" alt="image" src="https://github.com/user-attachments/assets/600ecfe1-7a27-4462-840e-7a9afffd6496" />

rds-sg chỉ cho phép 5432 từ ecs-sg:
<img width="1427" height="522" alt="image" src="https://github.com/user-attachments/assets/57afca36-1d3d-44d8-a488-adaeb7388424" />

### ECS task đang chạy
<img width="1410" height="557" alt="image" src="https://github.com/user-attachments/assets/f5d55b7a-e086-4da5-bae9-90dacba571d8" />

### API kết nối được RDS
<img width="961" height="326" alt="image" src="https://github.com/user-attachments/assets/65ba91ce-2b21-4bab-9baf-21f8bd7f17a7" />

### Swagger
<img width="947" height="866" alt="image" src="https://github.com/user-attachments/assets/d2e842a0-9777-4dae-ba6f-73666e954829" />

---

