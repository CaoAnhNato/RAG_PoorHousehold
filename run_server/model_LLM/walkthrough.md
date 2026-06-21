# Hướng dẫn Khởi chạy Llama-server

Tôi đã tạo thành công toàn bộ thư mục và các file cấu hình tại `run_server` để bạn có thể tải code về server cloud và chạy nhanh chóng.

## Cấu trúc thư mục hiện tại:
- `Dockerfile`: Chứa công thức build Image dựa trên `ghcr.io/ggerganov/llama.cpp:server-cuda` và cài đặt `hf_transfer`.
- `entrypoint.sh`: Kịch bản chịu trách nhiệm tải model siêu tốc và kích hoạt `llama-server` tự động.
- `docker-compose.yml`: File giúp triển khai 1-click có mount Volume (lưu cache file GGUF) và cấp quyền truy cập GPU.
- `.env.example`: Chứa biến môi trường `HF_TOKEN`.

## Các bước chạy trên Cloud Server (Ubuntu)

### Bước 1: Chuẩn bị `.env`
Bạn tải toàn bộ thư mục `run_server` về máy chủ. Mở terminal tại thư mục đó và copy file `.env`:
```bash
cp .env.example .env
```
Mở file `.env` (bằng `nano .env` hoặc `vim .env`) và thay `hf_YOUR_TOKEN_HERE` thành API key thực tế của bạn.

### Bước 2: Cấp quyền thực thi cho script
Đảm bảo file `entrypoint.sh` có quyền thực thi (thường là có sẵn vì tôi đã chạy lệnh `chmod` trong Dockerfile, nhưng phòng hờ nếu môi trường Github làm mất quyền):
```bash
chmod +x entrypoint.sh
```

### Bước 3: Khởi chạy bằng Docker Compose
Dùng lệnh sau để tự động build image, tải model và chạy server ở chế độ nền (background):
```bash
docker compose up -d --build
```

### Bước 4: Kiểm tra trạng thái
Bạn có thể xem trực tiếp tiến trình tải model và khởi chạy bằng lệnh:
```bash
docker compose logs -f
```
> [!TIP]
> Khi bạn thấy dòng chữ báo hiệu `llama server listening at http://0.0.0.0:8080`, điều đó có nghĩa là server đã sẵn sàng. Lần chạy đầu tiên sẽ mất thời gian để tải model, nhưng từ những lần chạy sau, model đã được lưu cache ở thư mục `models_cache` nên sẽ khởi động tức thì.

## Kiểm thử Server
Mở một terminal khác trên server cloud và chạy thử lệnh cURL sau để kiểm tra xem hệ thống sinh text generation có mượt không:
```bash
curl --request POST \
  --url http://localhost:8080/v1/chat/completions \
  --header "Content-Type: application/json" \
  --data '{
    "messages": [
      {
        "role": "user",
        "content": "Xin chào, bạn có thể tự giới thiệu về bản thân không?"
      }
    ]
  }'
```

> [!NOTE]
> Mọi tham số tối ưu (`--gpu-layers 999`, `--flash-attn`, `--ctx-size 16384`, `--batch-size 1024`) đã được cấu hình cứng trong `entrypoint.sh`. Nếu trong tương lai bạn đổi GPU hoặc muốn tuỳ biến, chỉ cần vào file `entrypoint.sh` sửa và chạy lại `docker compose restart`.
