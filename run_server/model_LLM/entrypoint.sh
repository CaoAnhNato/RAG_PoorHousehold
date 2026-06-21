#!/bin/bash
set -e

# Model repo từ cấu hình
MODEL_REPO="google/gemma-4-26B-A4B-it-qat-q4_0-gguf"
MODEL_DIR="/models"

echo "========================================================="
echo "Bắt đầu tải model từ Hugging Face..."
echo "Repo: $MODEL_REPO"
echo "Lưu ý: Tốc độ tải đã được tối ưu nhờ hf_transfer."
echo "========================================================="

# Tải model (chỉ tải các file *.gguf để tránh tải thừa các file không cần thiết)
huggingface-cli download $MODEL_REPO \
    --include "*.gguf" \
    --local-dir $MODEL_DIR \
    --local-dir-use-symlinks False

# Tìm đường dẫn file .gguf đầu tiên vừa được tải về
MODEL_FILE=$(ls $MODEL_DIR/*.gguf | head -n 1)

if [ -z "$MODEL_FILE" ]; then
    echo "Lỗi: Không tìm thấy file .gguf nào trong thư mục $MODEL_DIR sau khi tải."
    exit 1
fi

echo "========================================================="
echo "Khởi động llama-server..."
echo "Model: $MODEL_FILE"
echo "Thông số: gpu-layers=999, flash-attn=on, ctx-size=16384, batch-size=1024"
echo "========================================================="

# Khởi chạy llama-server. Trong base image, binary thường nằm tại /llama-server
exec /llama-server \
    -m "$MODEL_FILE" \
    --host 0.0.0.0 \
    --port 8080 \
    --gpu-layers 999 \
    --flash-attn \
    --ctx-size 16384 \
    --batch-size 1024
