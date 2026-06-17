FROM ghcr.io/ggerganov/llama.cpp:server-cuda

# Update package lists and install python3 and pip (needed for huggingface-cli)
RUN apt-get update && \
    apt-get install -y python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install huggingface_hub with hf_transfer for blazing fast downloads
RUN pip3 install -U "huggingface_hub[cli,hf_transfer]"

# Enable hf_transfer using environment variable
ENV HF_HUB_ENABLE_HF_TRANSFER=1

# Create a directory for models
RUN mkdir -p /models

# Copy the custom entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use the custom script as the container entrypoint
ENTRYPOINT ["/entrypoint.sh"]
