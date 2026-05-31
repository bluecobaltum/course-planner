#!/bin/bash
# 在 Windows 上运行此脚本（Git Bash），打包项目并上传到阿里云服务器
# 用法: bash pack.sh 47.xxx.xxx.xxx

SERVER_IP=${1:?请传入服务器 IP，例如: bash pack.sh 47.xxx.xxx.xxx}

echo "========== 1/3 打包项目 =========="
cd "$(dirname "$0")/.."

# 备份原始 API_BASE
cp frontend/src/api/schedule.ts frontend/src/api/schedule.ts.bak

# 修改 API_BASE 为同源（仅此一次，之后自动恢复）
sed -i 's|const API_BASE = .*|const API_BASE = "";|' frontend/src/api/schedule.ts

# 打包（排除 node_modules 和 __pycache__）
tar -czf deploy-package.tar.gz \
    --exclude='frontend/node_modules' \
    --exclude='frontend/dist' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='test' \
    --exclude='.git' \
    --exclude='部署' \
    backend/ \
    frontend/ \
    部署/deploy.sh

# 恢复本地文件
mv frontend/src/api/schedule.ts.bak frontend/src/api/schedule.ts

echo "========== 2/3 上传到服务器 =========="
scp deploy-package.tar.gz "root@${SERVER_IP}:/root/"
scp 部署/deploy.sh "root@${SERVER_IP}:/root/"

echo "========== 3/3 远程执行部署 =========="
ssh "root@${SERVER_IP}" "
    cd /root
    tar -xzf deploy-package.tar.gz
    chmod +x deploy.sh
    bash deploy.sh
"

echo "完成！访问 http://${SERVER_IP}"
