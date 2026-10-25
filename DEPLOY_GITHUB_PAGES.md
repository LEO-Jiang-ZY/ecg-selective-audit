# 把 lectrace 演示发布成 GitHub Pages 个人网页

> 目标：把 `lecture/01_audit.py` 变成 `https://<你的用户名>.github.io/<仓库名>/` 这样的公开链接，
> 任何人用浏览器就能按方向键逐步看模型执行。
>
> 关键事实：lectrace 的 `build` 会生成**纯静态文件**（HTML + JS + JSON 轨迹），不需要 Node.js、
> 不需要后端。所以「能不能上 GitHub Pages」只取决于你选哪种发布方式。

---

## 当前状态（2026-10-25 18:00）：仓库已建、已提交，待推送与开启 Pages

| 项 | 状态 |
|---|---|
| GitHub 账号 | `LEO-Jiang-ZY`（存在） |
| 远程仓库 | `github.com/LEO-Jiang-ZY/ecg-selective-audit`（public，**当前为空**） |
| 本地提交 | 已创建 `30efaf3`，79 个文件，等待 push |
| Pages | **未开启**（`has_pages: false`） |

**关键教训**：先点 Publish 但本地没有 commit，GitHub 只会建一个空仓库（`size: 0`），
文件并不会上传。必须**先 Commit，再 Push**。

### 现在只剩两步

1. 打开 GitHub Desktop → 顶部应显示 `1 commit to push` → 点 **Push origin**。
   推送完成后刷新仓库页面，应能看到 79 个文件（含 `docs/`）。
2. 仓库页 → **Settings → Pages** → Source: **Deploy from a branch**
   → Branch **main**，目录 **/docs** → **Save**。

### 正确网址（两个域名不要混）

| 用途 | 地址 |
|---|---|
| 仓库页（代码） | `https://github.com/LEO-Jiang-ZY/ecg-selective-audit` |
| 演示页（Pages） | `https://LEO-Jiang-ZY.github.io/ecg-selective-audit/` |

常见错误：把两者拼成 `github.com/LEO-Jiang-ZY.github.io/...` —— `github.com` 后面
只能是**用户名**，不能带 `.github.io`；而 `LEO-Jiang-ZY.github.io` 本身就是域名，
前面不再加 `github.com/`。

---

## 早期记录：仓库就绪，只剩点击发布

`D:/iAIM/lecture` 已经是 git 仓库（分支 `main`），**79 个文件已全部暂存（staged）**，
`_site/`、`docs/.lectrace_cache.json` 已写入 `.gitignore`。**不需要再执行任何 git 命令。**

已完成的验证：

- `docs/` 内全部为相对路径（`./assets/…`、`./traces/index.json`），可在
  `https://<用户名>.github.io/<仓库名>/` 这样的**子路径**下正常加载；
- 本地以父目录起服务模拟子路径部署，`index.html`、`traces/index.json`、1.5 MB 的主 JS 均返回 200；
- `docs/.nojekyll` 已放置，避免 GitHub Pages 的 Jekyll 处理干扰静态资源。

### 剩余步骤：GitHub Desktop 里 6 步

1. 打开 GitHub Desktop → **Sign in to GitHub.com**（未登录时先登录）。
2. **File → Add Local Repository…** → 选择 `D:\iAIM\lecture` → **Add**。
3. 左下角 Summary 填 `Initial commit: lectrace deck`，点 **Commit to main**。
4. 顶部点 **Publish repository**：仓库名填 `ecg-selective-audit`，
   **取消勾选 “Keep this code private”**（免费账号的 Pages 只对公开仓库开放）→ **Publish**。
5. 浏览器打开 `https://github.com/<你的用户名>/ecg-selective-audit` → **Settings → Pages**
   → Source 选 **Deploy from a branch** → Branch 选 **main**，目录选 **/docs** → **Save**。
6. 等 1–2 分钟，访问 `https://<你的用户名>.github.io/ecg-selective-audit/`。

### 仓库名决定网址

| 仓库名 | 发布后的地址 |
|---|---|
| `ecg-selective-audit` | `https://<用户名>.github.io/ecg-selective-audit/` |
| `<用户名>.github.io` | `https://<用户名>.github.io/`（根域名，仓库名必须与用户名完全一致） |

两种情况都把 Pages 源设成 `main` + `/docs` 即可，站内路径不受影响。

### 常见失败

| 现象 | 原因与处理 |
|---|---|
| 打开是 404 | Pages 还没构建完（看 Actions 里 `pages build and deployment` 是否绿色），或分支/目录选错 |
| 页面白屏 | F12 → Network 看哪个资源 404；通常是 `docs/assets/` 没提交完整 |
| 样式全丢、只有文字 | `.nojekyll` 没被提交（它在 `docs/` 里，确认 `git status` 可见） |
| 推送被拒 | 仓库是用网页端先建的空仓库且带 README；在 GitHub Desktop 里先 Pull 再 Push |

---

## 0. 先理解两种发布的区别

lectrace 的页面内容来自**执行轨迹**（JSON），而轨迹是跑脚本时录下来的。因此有两种做法：

| | 方案 A：本地构建，推送静态文件 | 方案 B：GitHub Actions 自动构建 |
|---|---|---|
| 谁跑 Python | 你的电脑 | GitHub 的服务器 |
| 需要上传什么 | `docs/`（26 MB 静态文件） | 源码 + 数据 + 模型权重 |
| 需要 CI 装 PyTorch | 不需要 | 需要（约 2–3 分钟下载，CPU 版） |
| 改内容后 | 本地重新 build → push | 直接 push，自动重建 |
| 适合 | **本项目推荐**（只有一讲，内容稳定） | 多讲、频繁更新、想让别人一键复现 |

本项目依赖 `torch`（State 2 要真实前向）和 `ptbxl` 包，方案 B 需要在 CI 里装 torch 并把
`code/` 和 `best.pt` 一起上传。方案 A 已经把这一切在本地做完，仓库里只有静态文件。

**下面先给方案 A 的完整步骤，方案 B 放在最后作为可选项。**

---

## 1. 需要装什么

| 工具 | 必要性 | 说明 |
|---|---|---|
| **Git for Windows** | 必须 | <https://git-scm.com/download/win>，装完在终端能用 `git --version` |
| **GitHub 账号** | 必须 | 免费账号即可，Pages 对公开仓库免费 |
| **GitHub Desktop** | 可选，推荐给不熟命令行的人 | 图形化提交/推送，省掉 `git` 命令记忆 |
| **GitHub CLI (`gh`)** | 可选 | 一条命令建仓库：`gh repo create` |
| **VS Code** | 可选 | 内置 Git 面板，改完源码直接提交 |
| Node.js | **不需要** | lectrace 自带打包好的 React 前端 |
| Python | 只在本地 build 时需要 | 你已经有了（`envs/ptbxl`） |

> 本机已具备 git（Git Bash 自带 `git 2.55`），并已安装 GitHub Desktop。
> 上述步骤 2–6 直接在 GitHub Desktop 图形界面完成即可，无需命令行。

---

## 2. 方案 A：本地构建 → 推送 `docs/`

### 2.1 确认构建产物

我已在 `lecture/docs/` 生成好站点（26 MB，含 `index.html`、`assets/`、`traces/`）。
本地预览：

```bash
cd D:/iAIM/lecture/docs
python -m http.server 8788 --bind 127.0.0.1
# 浏览器打开 http://127.0.0.1:8788
```

### 2.2 在 GitHub 建仓库

网页方式：GitHub → New repository → 名称填 `ecg-selective-audit` → **Public** →
不要勾选 "Add a README"（避免和本地冲突）→ Create。

或者用 GitHub CLI：

```bash
gh repo create ecg-selective-audit --public --source=. --remote=origin
```

### 2.3 初始化本地仓库并推送

在 `D:/iAIM/lecture` 目录下执行（注意：把仓库根设成 `lecture/`，而不是整个 `D:/iAIM`，
否则会把 1 GB 数据集和结果文件一起传上去）：

```bash
cd D:/iAIM/lecture

# 只保留要发布的东西
cat > .gitignore <<'EOF'
_site/
__pycache__/
*.pyc
EOF

git init
git add 01_audit.py SPEAKER_SCRIPT.md demo/ assets/ docs/ .gitignore
git commit -m "lectrace walkthrough: calibration is not enough"
git branch -M main
git remote add origin https://github.com/<你的用户名>/ecg-selective-audit.git
git push -u origin main
```

> `demo/` 只有 100 KB（一条 ECG 样本 + 2,198 条 logits），`assets/` 是图，`docs/` 是构建产物。
> 总大小约 27 MB，远低于 GitHub 单文件 100 MB 和仓库建议 1 GB 的限制。

### 2.4 打开 Pages

仓库 → **Settings** → 左侧 **Pages**：

- **Source**：`Deploy from a branch`
- **Branch**：`main`，目录选 **`/docs`**
- Save

等 1–2 分钟，页面顶部会出现
`Your site is live at https://<用户名>.github.io/ecg-selective-audit/`。

### 2.5 以后怎么更新

```bash
cd D:/iAIM/lecture
# 改完 01_audit.py 后重新构建
"C:/Users/24958/.workbuddy/binaries/python/envs/ptbxl/Scripts/lectrace.exe" build --output docs
git add docs
git commit -m "update lecture"
git push
```

Pages 会在一分钟内自动刷新。**注意 `docs/` 必须提交**，因为 Pages 直接读它。

---

## 3. 方案 B：GitHub Actions 自动构建（可选）

如果你希望「push 源码 → 自动重建」，把仓库根设成 `D:/iAIM`（含 `code/`、`lecture/`、
`result/runs/seed_42/best.pt`），并加入下面这个 workflow。

`.github/workflows/lectrace.yml`：

```yaml
name: Build and deploy lectrace

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install CPU torch (large, cached below)
        uses: actions/cache@v4
        id: torch-cache
        with:
          path: ~/.cache/pip
          key: torch-cpu-2.5.1

      - run: pip install --upgrade pip
      - run: pip install lectrace numpy scipy pyyaml
      - run: pip install torch --index-url https://download.pytorch.org/whl/cpu

      - name: Build
        working-directory: lecture
        run: lectrace build --output _site

      - uses: actions/upload-pages-artifact@v3
        with:
          path: lecture/_site

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

然后在 **Settings → Pages → Source** 里选 **GitHub Actions**（不是 branch）。

三个必须注意的点：

1. **必须上传 `result/runs/seed_42/best.pt`**（216 KB）和 `code/src/ptbxl/`，否则脚本 import 失败。
2. **必须上传 `lecture/demo/`**（ECG 样本与 logits），否则 State 1 和 State 4 没有数据。
3. `01_audit.py` 里用 `Path(__file__).resolve().parent` 定位资源，所以只要 `lecture/` 的相对结构不变就能跑。

如果嫌 torch 太重，可以给 CI 用一份**轻量版脚本**：State 2 不加载模型，改为读取预存的
中间张量（`demo/forward_trace.npz`），这样 CI 只需 `numpy scipy pyyaml`。要我生成这版可以再说。

---

## 4. 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| 页面 404 | Pages 的目录选错 | Source 选 branch 时目录必须是 `/docs`；选 Actions 时不要选 branch |
| 页面白屏、控制台报 404 取 `traces/01_audit.json` | 只推了 `index.html`，没推 `traces/` | `git add docs` 要包含全部子目录 |
| 图片不显示 | `assets/` 未提交，或路径大小写不符 | Linux Pages 区分大小写，确认文件名一致 |
| 推送被拒（>100 MB） | 把数据集或 `result/cache` 带进去了 | 仓库根只设到 `lecture/`，或用 `.gitignore` 排除 |
| 中文显示为方块 | 浏览器字体问题，不是构建问题 | 页面本身是英文，通常不会遇到 |
| 更新后页面没变 | Pages 有 CDN 缓存 | 强制刷新（Ctrl+Shift+R），或等 1–2 分钟 |

---

## 5. 一句话总结

装 Git → 在 `lecture/` 建仓库 → 提交 `01_audit.py demo/ assets/ docs/` → Pages 选 `main /docs`。
不需要 Node.js，不需要后端，不需要在云端装 PyTorch。
