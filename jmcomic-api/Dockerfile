FROM python:3.10-slim

WORKDIR /app

# 复制应用代码
COPY main.py .

# 安装依赖
RUN pip install jmcomic fastapi uvicorn pydantic img2pdf

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 9080

# 运行应用
CMD ["python", "main.py"]
