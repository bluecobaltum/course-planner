# AI 智能选课助手 — 阿里云部署指南

## 需要准备

1. 阿里云 ECS 服务器一台（Ubuntu 22.04，2核4G 以上）
2. 服务器公网 IP，例如 `47.xxx.xxx.xxx`
3. SSH 能连上服务器（`ssh root@47.xxx.xxx.xxx`）

---

## 方式 A：自动部署（推荐）

### 1. 在 Windows 上打开 Git Bash，运行：

```bash
cd "c:/Users/34356/Desktop/黑客松"
bash 部署/pack.sh 47.xxx.xxx.xxx
```

把 `47.xxx.xxx.xxx` 换成你的服务器 IP。

这个脚本会自动：
- 打包项目
- 上传到服务器
- 安装所有依赖
- 构建前端
- 配置 Nginx
- 启动后端

---

### 2. 配置 API Key

部署完成后 SSH 到服务器：

```bash
ssh root@47.xxx.xxx.xxx
nano /root/backend/.env
```

把 `OPENAI_API_KEY=QC-你的密钥` 改成真实密钥，保存。

重启后端：

```bash
cd /root/backend
pkill -f "uvicorn main:app"
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /var/log/course-planner.log 2>&1 &
```

---

### 3. 安全组放行

阿里云控制台 → ECS → 安全组 → 入方向 → 添加：

| 端口 | 协议 | 来源 | 说明 |
|------|------|------|------|
| 80 | TCP | 0.0.0.0/0 | 网页访问 |
| 443 | TCP | 0.0.0.0/0 | HTTPS（可选）|
| 22 | TCP | 你的IP | SSH |

---

### 4. 访问

浏览器打开 `http://47.xxx.xxx.xxx`

---

## 方式 B：手动部署

如果把 `deploy-package.tar.gz` 放到服务器上手动解压：

```bash
cd /root
tar -xzf deploy-package.tar.gz
bash deploy.sh
```

然后按上面第 2-4 步操作。

---

## 更新代码

后续改了代码后，重新运行：

```bash
bash 部署/pack.sh 47.xxx.xxx.xxx
```

或者只更新后端：

```bash
scp -r backend/ root@47.xxx.xxx.xxx:/root/
ssh root@47.xxx.xxx.xxx "cd /root/backend && pkill python3; nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &"
```

只更新前端：

```bash
cd frontend && npm run build
scp -r dist/ root@47.xxx.xxx.xxx:/var/www/html/
```

---

## 查看日志

```bash
ssh root@47.xxx.xxx.xxx
tail -f /var/log/course-planner.log
```
