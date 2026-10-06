# 给刘若汐

一个单文件网页：打字机文案 + 「惊喜」按钮（满屏小爱心）。

## 线上地址

**https://tavis-jiang.github.io/roux/**

## 文件

| 文件 | 说明 |
|---|---|
| `index.html` | 页面本体。改顶部 `CONFIG` 块就能改文案、照片、音乐、爱心数量 |
| `hearts.py` | 同款满屏爱心的 Python 全屏版（纯标准库 tkinter，零依赖，可直接发给她运行） |
| `deploy.sh` | 一键发布 |

## 怎么改内容然后发布

```bash
# 1. 改 index.html 顶部 CONFIG
# 2. 发布
./deploy.sh "改了文案"
```

`deploy.sh` 会把改动同时推到 `main` 和 `gh-pages`。**GitHub Pages 是从 `gh-pages` 分支发布的**，
所以必须推 `gh-pages` 才会生效，只推 `main` 不会更新网站。

## 为什么不用 GitHub Actions

原本配了 Actions 自动部署，但新账号的 `GITHUB_TOKEN` 默认只读，
`actions/configure-pages` 的 `enablement: true` 拿不到 `pages: write`，直接失败。
改用 `gh-pages` 分支发布，更省事也更稳。

如果想换成 Actions 自动部署：仓库 Settings → Actions → General →
Workflow permissions 选 **Read and write permissions** → Save，然后告诉我，我把工作流加回来。

## 绑定自定义域名（可选，需要先买域名）

1. **注册域名** —— `lovelrx.life` 目前没人注册，去任意注册商买（Porkbun / Cloudflare / 阿里云 / 腾讯云）
2. **加 DNS 记录**（在域名注册商后台）：
   ```
   A     @     185.199.108.153
   A     @     185.199.109.153
   A     @     185.199.110.153
   A     @     185.199.111.153
   CNAME www   tavis-jiang.github.io
   ```
3. **仓库里绑定** —— Settings → Pages → Custom domain 填 `lovelrx.life` → Save
4. 等证书签发（几分钟到几小时），然后勾上 **Enforce HTTPS**

绑定成功后地址就变成 `https://lovelrx.life/`。
