# 一键部署脚本

export DEBIAN_FRONTEND=noninteractive

echo "========== 1/8 更新系统 =========="
apt update -qq && apt upgrade -y -qq

echo "========== 2/8 安装 Python 环境 =========="
apt install -y -qq python3 python3-pip python3-venv
pip3 install -q fastapi uvicorn pydantic openpyxl openai python-dotenv python-multipart ortools

echo "========== 3/8 安装 Node.js 18 =========="
if command -v node &>/dev/null; then
    echo "Node.js $(node -v) 已安装"
else
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y -qq nodejs
fi

echo "========== 4/8 安装 Nginx =========="
apt install -y -qq nginx

echo "========== 5/8 配置环境 =========="
# 如果 .env 不存在，用模板创建
if [ ! -f /root/backend/.env ]; then
    if [ -f /root/.env ]; then
        cp /root/.env /root/backend/.env
        echo "已复制 .env 到 backend 目录"
    else
        cat > /root/backend/.env << 'EOF'
# AIPING API 配置
OPENAI_API_KEY=QC-你的密钥
OPENAI_BASE_URL=https://aiping.cn/api/v1
IMAGE_PROVIDER=qwen
LLM_EVAL_MODEL=DeepSeek-V4-Flash
EOF
        echo "提示: 请编辑 /root/backend/.env 填入真实 API Key"
    fi
fi

# 设置 api base url
sed -i 's|const API_BASE = "http://localhost:8000"|const API_BASE = ""|' /root/frontend/src/api/schedule.ts

echo "========== 6/8 构建前端 =========="
cd /root/frontend
npm install
npx vite build --quiet
mkdir -p /var/www/html
cp -r dist/* /var/www/html/

echo "========== 7/8 配置 Nginx =========="
cat > /etc/nginx/sites-available/course-planner << 'NEOF'
server {
    listen 80;
    server_name _;
    root /var/www/html;
    index index.html;

    # API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_read_timeout 120s;
        proxy_buffering off;
    }

    # 前端 SPA
    location / {
        try_files $uri /index.html;
    }
}
NEOF

rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/course-planner /etc/nginx/sites-enabled/
nginx -t && nginx -s reload 2>/dev/null || nginx

echo "========== 8/8 启动后端 =========="
pkill -f "uvicorn main:app" 2>/dev/null || true
cd /root/backend
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /var/log/course-planner.log 2>&1 &

sleep 2
if curl -s http://localhost:8000/api/health | grep -q ok; then
    echo ""
    echo "=============================================="
    echo "  部署完成！"
    echo "  后端: http://$(curl -s ifconfig.me):8000"
    echo "  前端: http://$(curl -s ifconfig.me)"
    echo "=============================================="
else
    echo "后端启动失败，查看日志: tail -f /var/log/course-planner.log"
fi
