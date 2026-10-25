# 用 Vercel 发布（与同学站点同样的访问形态）

`https://tox21-error-risk-signals.vercel.app/` 这类地址来自 **Vercel**：把仓库连上去，
它按你指定的输出目录做静态托管，自动签发 HTTPS 证书，并给出 `<项目名>.vercel.app` 域名。

我们的情况不需要任何构建步骤：`docs/` 已经是 lectrace `build` 出来的成品，
所以 Vercel 只做一件事——把这个目录原样发出去。

---

## 方式一：网页导入（推荐，一次配置）

1. 打开 <https://vercel.com> → **Sign up** → 选 **Continue with GitHub**，授权后登录。
2. 控制台右上 **Add New… → Project** → 在列表里找到 `ecg-selective-audit` → **Import**。
3. 配置页只改一处：

   | 字段 | 填什么 |
   |---|---|
   | Framework Preset | **Other** |
   | Root Directory | `./`（默认） |
   | Build Command | 留空（若显示为灰色 `npm run build`，点 **Override** 后清空） |
   | Output Directory | **`docs`** |
   | Install Command | 留空 |

   仓库根目录已有 `vercel.json`，其中写了 `"outputDirectory": "docs"` 与
   `"framework": null`，所以即使界面没读到，部署也会按这个走。

4. **Deploy**。约 30 秒后得到 `https://ecg-selective-audit.vercel.app/`。
5. 想换更好记的名字：Project → **Settings → General → Project Name** 改名，
   域名随之变成 `<新名字>.vercel.app`。

每次 push 到 `main` 都会自动重新部署。

## 方式二：命令行（不建 Project 也能发）

```bash
cd D:/iAIM/lecture
npx vercel@latest login      # 浏览器授权一次
npx vercel@latest --prod     # 按 vercel.json 上传
```

仓库里的 `vercel.json` 已声明输出目录，CLI 不会再追问框架类型。

---

## 与 GitHub Pages 的差别

| | GitHub Pages | Vercel |
|---|---|---|
| 地址形态 | `<用户名>.github.io/<仓库>` | `<项目名>.vercel.app` |
| 首次配置 | Settings → Pages → 选分支与目录 | 导入仓库 → 填输出目录 |
| 构建能力 | 只能托管静态文件 | 可跑构建（我们不需要） |
| 部署触发 | push 后由 Actions 构建 | push 后自动构建 |
| 大文件 | 仓库 1 GB / 单文件 100 MB 软限制 | 静态资源走 CDN，无同类限制 |
| 私有仓库 | Pages 需付费计划 | Hobby 免费档即可 |
| 国内访问 | 时快时慢 | 视网络，通常更稳 |

两者不冲突：可以同时开，哪个快用哪个。内容都是 `docs/`，不需要改代码。

---

## 常见问题

| 现象 | 原因 |
|---|---|
| 部署成功但打开是 404 | Output Directory 没填 `docs`，Vercel 发的是仓库根目录 |
| 构建失败 `No Output Directory named "public"` | 同上，且框架预设被识别成了某个前端框架，改成 **Other** |
| 页面能开、样式全丢 | `docs/assets/` 没被提交；本地 `git status` 确认无误后重新 push |
| 每次 push 都触发全量部署 | 正常行为；`docs/` 只在该目录变化时才需要重发，可在 Settings → Git 里设 Ignored Build Step |

---

## 若要复刻同学的「首页 + 子路径演示」结构

同学站点的组织形式是：

```
/                index.html + styles.css + script.js   ← 手写的项目介绍页
/lectrace/       lectrace 构建产物                     ← 交互演示
```

我们目前把 `docs/` 直接当站点根，打开即演示。若要同样分两层，做法是：

1. 在仓库根新建一个 `site/index.html` 作为介绍页（可用海报内容改写）；
2. 把 lectrace 产物放在 `site/lectrace/`；
3. `vercel.json` 的 `outputDirectory` 改为 `"site"`。

这样 `https://<项目>.vercel.app/` 是介绍页，`/lectrace/` 是演示页。
