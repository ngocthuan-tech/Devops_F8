# Bài tập buổi 8 - Thiết kế mạng nội bộ VPC

## Đề bài

Công ty có 2 team riêng biệt, mỗi team làm 1 microservice cho cùng 1 hệ thống chung:
- 2 service: order service và payment service
- Mỗi service có 1 database riêng
- Mỗi service có thể code bằng ngôn ngữ khác nhau
- Hệ thống dùng trong nội địa Nhật Bản

Yêu cầu: vẽ sơ đồ mạng (VPC, route table, subnet, NAT, NACL...) và chỉ ra các thông số region, AZ, dải IP, subnet.
## 1. Sơ đồ mạng

<img width="1500" height="1180" alt="image" src="https://github.com/user-attachments/assets/bbc598ab-04a3-4970-85c0-bd40604c2b2d" />

### Chú thích
| Số | Tên | Là gì |
|---|---|---|
| (1) | Region | Vùng địa lý đặt hạ tầng. Chọn Tokyo vì người dùng ở Nhật, gần thì nhanh |
| (2) | VPC | Mạng riêng của mỗi team. Mỗi service 1 VPC riêng, team này không đụng được mạng team kia |
| (3) | Internet Gateway | Cổng nối VPC ra Internet, mỗi VPC có 1 cái |
| (4) | AZ | Availability Zone, là các trung tâm dữ liệu khác nhau trong cùng region. Dùng 2 AZ để 1 cái chết thì cái kia vẫn chạy |
| (5) | Public subnet | Subnet ra vào Internet trực tiếp. Chỉ đặt ALB (nhận request từ khách) và NAT Gateway |
| (6) | Private subnet (app) | Chỗ chạy code của service. Bên ngoài không gọi thẳng vào được, muốn ra Internet thì đi qua NAT Gateway |
| (7) | Private subnet (DB) | Chỗ đặt database. Không ra Internet, chỉ app trong cùng VPC mới gọi được |
| (8) | VPC Peering | Đường nối riêng giữa 2 VPC để order service gọi được sang payment service |

---

## 2. Thông số

### Region, AZ, VPC

| | VPC Order | VPC Payment |
|---|---|---|
| Region | ap-northeast-1 (Tokyo) | ap-northeast-1 (Tokyo) |
| AZ | ap-northeast-1a, ap-northeast-1c | ap-northeast-1a, ap-northeast-1c |
| CIDR | 10.10.0.0/16 | 10.20.0.0/16 |
| Database | RDS PostgreSQL (Multi-AZ) | RDS MySQL (Multi-AZ) |

2 VPC dùng 2 dải IP khác nhau (10.10 và 10.20) vì muốn peering được thì CIDR không được trùng.

### Subnet

Mỗi subnet là /24 = 256 IP, AWS giữ lại 5 IP nên còn 251 IP dùng được.

| Subnet | Order | Payment | AZ |
|---|---|---|---|
| public-1a | 10.10.1.0/24 | 10.20.1.0/24 | 1a |
| public-1c | 10.10.2.0/24 | 10.20.2.0/24 | 1c |
| app-1a | 10.10.11.0/24 | 10.20.11.0/24 | 1a |
| app-1c | 10.10.12.0/24 | 10.20.12.0/24 | 1c |
| db-1a | 10.10.21.0/24 | 10.20.21.0/24 | 1a |
| db-1c | 10.10.22.0/24 | 10.20.22.0/24 | 1c |

Cách đánh số: public là 1, 2; app là 11, 12; DB là 21, 22. Chừa khoảng trống ở giữa để sau này thêm subnet.

### NAT Gateway

Mỗi VPC có 2 NAT Gateway, đặt ở public-1a và public-1c. Mỗi AZ dùng NAT của chính nó, nếu 1 AZ sập thì AZ còn lại vẫn ra Internet bình thường.

### Route table (VPC Order, VPC Payment làm giống vậy, đổi 10.10 ↔ 10.20)

| Route table | Gắn với subnet | Destination → Target |
|---|---|---|
| rt-public | public-1a, public-1c | 10.10.0.0/16 → local<br>0.0.0.0/0 → Internet Gateway |
| rt-app-1a | app-1a | 10.10.0.0/16 → local<br>0.0.0.0/0 → NAT Gateway 1a<br>10.20.0.0/16 → VPC Peering |
| rt-app-1c | app-1c | 10.10.0.0/16 → local<br>0.0.0.0/0 → NAT Gateway 1c<br>10.20.0.0/16 → VPC Peering |
| rt-db | db-1a, db-1c | 10.10.0.0/16 → local |

Chỉ subnet app có route sang VPC bên kia, subnet DB thì chỉ có local nên database không bị lộ ra ngoài.

### Security Group

| Security Group | Inbound cho phép |
|---|---|
| sg-alb-order | 443 từ 0.0.0.0/0 |
| sg-app-order | 8080 từ sg-alb-order |
| sg-db-order | 5432 từ sg-app-order |
| sg-app-payment | 8080 từ 10.10.11.0/24, 10.10.12.0/24 (chỉ order service) |
| sg-db-payment | 3306 từ sg-app-payment |

### NACL

NACL là stateless nên phải mở thêm port 1024-65535 cho chiều trả về.

| NACL | Inbound | Outbound |
|---|---|---|
| nacl-public | 443 từ 0.0.0.0/0<br>1024-65535 từ 0.0.0.0/0 | All |
| nacl-app | 8080 từ dải public của VPC mình<br>8080 từ dải app của VPC Order (chỉ bên Payment)<br>1024-65535 từ 0.0.0.0/0 | All |
| nacl-db | 5432 / 3306 từ dải app của VPC mình | 1024-65535 tới dải app của VPC mình |

---

## 3. Giải thích sơ đồ

Mình chọn region Tokyo vì hệ thống chỉ dùng ở Nhật, đặt server gần người dùng thì độ trễ thấp nhất. Trong region đó mình dùng 2 AZ là 1a và 1c, mọi thứ đều được nhân đôi ở 2 AZ để nếu 1 AZ gặp sự cố thì hệ thống vẫn chạy.

Đề nói 2 team hoàn toàn riêng biệt nên mình tách mỗi service ra 1 VPC riêng. Team order không vào được mạng của team payment và ngược lại. Nhưng order service vẫn cần gọi payment service để thanh toán, nên mình nối 2 VPC lại bằng VPC Peering, và chỉ mở đúng route từ subnet app bên này sang subnet app bên kia.

Trong mỗi VPC mình chia làm 3 tầng. Tầng public chỉ để ALB nhận request từ khách và NAT Gateway cho các server bên trong đi ra Internet. Tầng app là nơi chạy code, nằm trong private subnet nên ngoài Internet không gọi thẳng vào được, phải đi qua ALB. Tầng DB nằm trong cùng, không có đường ra Internet, chỉ app trong cùng VPC mới kết nối được. Làm vậy để database an toàn nhất.

Việc mỗi service code bằng ngôn ngữ khác nhau thì không ảnh hưởng tới thiết kế mạng, vì mạng chỉ quan tâm IP và port. Mỗi service có database riêng nên mình cho order dùng PostgreSQL, payment dùng MySQL, đặt mỗi cái trong private subnet DB của VPC mình.

Luồng chạy của 1 request:
1. Khách gọi API → Internet Gateway → ALB ở public subnet
2. ALB chuyển vào order service ở private subnet app
3. Order service lưu đơn hàng vào PostgreSQL
4. Order service gọi payment service qua VPC Peering
5. Payment service lưu giao dịch vào MySQL, nếu cần gọi cổng thanh toán bên ngoài thì đi ra qua NAT Gateway
