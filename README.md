# Wheel-legged body leveling

基于项目 poster v11.25 的静态研究展示网站。保留学术版排版、真实 CAD 与 UI 截图、实验数据和四段完整比较视频，围绕 Recording 与 Residual PPO。

## 本地预览

安装 Node.js 20 或更新版本后，在此目录运行：

```sh
node scripts/build.mjs
node scripts/check.mjs
node scripts/serve.mjs
```

浏览器打开 `http://127.0.0.1:4173`。无需安装额外 JavaScript 依赖。`/project-preview/` 可检查项目仓库子路径；此地址只用于本地检查。

## 发布到 GitHub Pages

1. 将本目录内容上传到自己的 GitHub 仓库，默认分支使用 `main`。保留 `.github/workflows/pages.yml`。
2. 在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。
3. 推送到 `main` 会自动构建、检查并发布。也可在 **Actions → Deploy static research showcase → Run workflow** 手动启动。
4. 等待部署成功，以 GitHub 返回的实际 Pages 网址为准。发布后匿名检查图片、视频、下载和锚点，再生成该网址的最终二维码。

用户站点仓库与项目站点仓库的地址结构不同；本项目采用相对资源路径，两者均可使用。无需主题模板、服务端、登录或自定义域名。仓库名可以使用 `wheel-legged-body-leveling`。默认网址仍包含 GitHub 分配的 `github.io` 域名；若要独立域名，需要自行拥有并配置该域名。

四个 MP4 都是完整 H.264 视频，每个小于 20 MB，可直接随此项目上传；不要使用 Git LFS 指针或仓库文件页充当视频地址。播放器按需加载。视频流量较大时可改为经匿名播放验证的稳定公共媒体地址。

## 日常维护

- `content/site.json`：项目身份、视频路径、条件、说明，以及待补录的 `recordingDemo`。
- `content/training.json`：50 mm 与 100 mm 使用一致字段结构的真实训练阶段。
- `content/methods.json`：策略观测、动作范围、网络、奖励和训练参数。构建自动生成公开方法摘要。
- `content/research-figures.json`：数据图路径、图注、来源与解读。
- `scripts/build-academic.mjs`：页面结构及较长文案；`scripts/build.mjs` 是构建入口。
- `public/academic.css`、`public/app.js`：视觉样式和浏览器交互。
- `public/media/`：CAD、UI 截图、视频和封面。
- `public/figures/`、`public/data/`：科研图、CSV、指标与来源信息。

修改后重新构建和检查。不要直接编辑生成的 `dist/`。界面操作录屏由作者手动提供；公开页面保留明确标识的预留区域。补录时将 MP4 与封面放入 `public/media/`，并设置 `recordingDemo` 的 `title`、`src`、`poster`、`duration` 和 `description`。

## 数据与材料说明

100 mm CSV 有 94 条方法—条件记录，即两个方法 ×（39 个已知条件 + 8 个留出条件），不是 94 个独立条件。倾斜姿态配对图仅取双方严格成功的 25 个和 5 个配对条件；失败试验仍保留在下载表中。几何完成窗口与完整运行窗口分别列出。

`scripts/generate-research-figures.py` 可从随站 CSV 重绘四组 100 mm 数据图，需要 Python、numpy、pandas 和 matplotlib。50 mm 参考曲线和原始阶段图已有 PNG/SVG，保留其出处与限制，不把重绘称为新实验。

`public/documents/research-poster-v11-25.pdf` 是未经改动的原 poster，其旧二维码指向编辑页面，不能作为新 GitHub 网站的二维码使用。应在新网址验证后替换 poster 的二维码。此迁移包没有包含旧托管平台身份、凭据或内部审核材料。
