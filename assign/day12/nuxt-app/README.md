# Bài tập buổi 12 - Deploy Nuxt.js lên S3 + CloudFront

## Đề bài

- Dựng 1 dự án Nuxt.js và deploy sử dụng S3 + CloudFront
- Gửi link CloudFront

---

## Link CloudFront

https://dvr1gtqqsdfy.cloudfront.net

---

## Kiến trúc

```
Người dùng
   │  https://dvr1gtqqsdfy.cloudfront.net
   ▼
CloudFront (day12_nuxt, Free plan)
   │  HTTPS, cache ở edge gần người dùng
   │  Origin Access Control (OAC)
   ▼
S3 bucket tu-day12-nuxt-2026 (ap-southeast-1)
   - Block all public access: On
   - Bucket policy chỉ cho phép CloudFront đọc
   - Chứa web tĩnh build từ Nuxt (index.html, _nuxt/...)
```

- Nuxt build bằng `npm run generate` ra web tĩnh (HTML/CSS/JS) trong `.output/public`. S3 chỉ lưu được file tĩnh, không chạy được server Node, nên dùng `generate` chứ không dùng `build`.
- S3 để private, người dùng không vào thẳng S3 được mà phải đi qua CloudFront.
- CloudFront đọc S3 bằng OAC, có HTTPS sẵn với domain `*.cloudfront.net`, và cache file ở các edge location nên tải nhanh.
- Default root object = `index.html` để khi vào link gốc thì trả về trang chủ.

---

## Cấu trúc thư mục

```
day12/
├── Readme.md
└── nuxt-app/
    ├── app/app.vue        # trang chủ
    ├── nuxt.config.ts
    ├── package.json
    └── ...
```

---

## Các bước làm

### 1. Tạo project Nuxt
```bash
npm create nuxt@latest nuxt-app
cd nuxt-app
npm run dev        # chạy thử ở http://localhost:3000
```
Sửa trang chủ trong `app/app.vue`.

### 2. Build ra web tĩnh
```bash
npm run generate
```
Kết quả nằm trong `.output/public`, gồm `index.html`, `200.html`, `404.html`, `favicon.ico`, `robots.txt`, `_payload.json` và thư mục `_nuxt/`.

### 3. Tạo S3 bucket và upload
- Bucket: `tu-day12-nuxt-2026`, region `ap-southeast-1` (Singapore)
- Giữ **Block all public access** (bucket private)
- Upload toàn bộ nội dung **bên trong** `.output/public` lên tầng ngoài cùng của bucket (không upload nguyên thư mục `public`)

### 4. Tạo CloudFront distribution
- Plan: **Free**
- Origin: S3 bucket `tu-day12-nuxt-2026`
- Chọn **Allow private S3 bucket access to CloudFront** (OAC), CloudFront tự cập nhật bucket policy
- Domain riêng: không dùng, dùng domain mặc định `*.cloudfront.net`
- Sau khi tạo: sửa **Default root object = `index.html`**

### 5. Kiểm tra
- Mở link CloudFront: trang hiện ra, nút bấm chạy được
- Mở thẳng link S3: bị **AccessDenied**, đúng như mong muốn vì bucket private

### Khi cập nhật web
```
Sửa code → npm run generate → upload lại lên S3 → CloudFront tạo Invalidation "/*"
```
Invalidation để xóa cache cũ ở edge, người dùng thấy bản mới ngay.

---

## Minh chứng

### 1. Tạo S3 bucket
<img width="655" height="205" alt="image" src="https://github.com/user-attachments/assets/623a35dc-02a1-4072-b56a-a8e886d4b917" />

### 2. Upload web tĩnh lên S3
<img width="646" height="650" alt="image" src="https://github.com/user-attachments/assets/51e8560c-7179-4eee-bc3e-110168ccdb1f" />


### 3. Tạo CloudFront distribution
<img width="658" height="276" alt="image" src="https://github.com/user-attachments/assets/859bd02b-2e72-4163-8d5f-587943edf8e1" />


### 4. Trang web chạy qua CloudFront
<img width="665" height="240" alt="image" src="https://github.com/user-attachments/assets/58f1fdf1-c281-40ce-a4fc-68eba7195490" />


### 5. Distribution đang hoạt động
<img width="658" height="115" alt="image" src="https://github.com/user-attachments/assets/96fde3a9-ae2b-4c4a-b45f-38c7ffa2553b" />


### 6. Truy cập thẳng S3 bị chặn
<img width="630" height="134" alt="image" src="https://github.com/user-attachments/assets/bbe86562-47e9-4c42-8133-5b20e65c754e" />


Ảnh này chứng minh bucket S3 để private, người dùng chỉ xem được web qua CloudFront.

---

## Ghi chú

- Gặp lỗi *"Your account must be verified before you can add new CloudFront resources"* khi tạo distribution lần đầu. Em đã gửi case cho AWS Support để xác minh tài khoản, sau đó tạo lại được bình thường.
- CloudFront dùng gói Free ($0/tháng), S3 chỉ chứa vài trăm KB nên chi phí gần như bằng 0. Link để chạy luôn, không cần xóa.
