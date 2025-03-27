FROM public.ecr.aws/lambda/python:3.13

# Install system dependencies
RUN dnf update -y && \
    dnf install -y \
    freetype-devel \
    libjpeg-turbo-devel \
    zlib-devel \
    gcc \
    make \
    python3-devel \
    fontconfig && \
    dnf clean all

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Create necessary directories
RUN mkdir -p /tmp/certificates && \
    chmod 777 /tmp/certificates

# Set environment variables
ENV PYTHONPATH=${LAMBDA_TASK_ROOT}
ENV FONTCONFIG_PATH=/etc/fonts
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the CMD to your handler
CMD [ "lambda_function.lambda_handler" ]
