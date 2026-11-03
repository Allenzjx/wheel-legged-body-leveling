# Residual PPO for Body Leveling of Wheel-Legged Robots During Obstacle Traversal

机器人项目的静态研究网站，围绕 Recording 与 50 mm Residual PPO 整体控制框架。首页前置 100 mm 名义条件对比视频，下方保留按 50 mm、100 mm 和失败案例分类的视频。

## 公开网站

- 网站：https://allenzjx.github.io/wheel-legged-body-leveling/
- 源码：https://github.com/Allenzjx/wheel-legged-body-leveling
- 2026-10-31 已通过 GitHub Actions 在 Linux 上构建、检查并部署；43 项匿名网页与素材检查通过，视频支持分段请求并已在浏览器实际播放。
- 网站可直接访问，无需 GitHub 登录。今后向 `main` 推送内容更新会自动发布。

UI 操作录屏仍由作者补录，页面已标明预留位置。所有迁移内容沿用已核实的数据与素材。

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
- `research/current-results.json`：当前正文采用的已核实结果、适用范围和数据来源。
- `research/README.md`：数据口径、模型、视频和历史记录说明。
- `scripts/build-report.mjs`：页面结构及较长文案；`scripts/build.mjs` 是构建入口。
- `public/academic.css`、`public/app.js`：视觉样式和浏览器交互。
- `public/media/`：CAD、UI 截图、视频和封面。
- `research/archive/2026-10-31/`：历史科研图、CSV、方法配置与来源信息，仅在 GitHub 供查阅，不进入网站构建输出。

修改后重新构建和检查。不要直接编辑生成的 `dist/`。界面操作录屏由作者手动提供；公开页面保留明确标识的预留区域。补录时将 MP4 与封面放入 `public/media/`，并设置 `recordingDemo` 的 `title`、`src`、`poster`、`duration` 和 `description`。

## 数据与材料说明

当前网页采用100 mm已知39条件的 common completion：Recorded Replay 31/39，Residual PPO 37/39。该计数与各方法的 native success 或两者交集不同。50 mm方法介绍与100 mm实验各自保留适用范围。

历史100 mm CSV有94条方法—条件记录，即两个方法 ×（39个已知条件 + 8个留出条件）。归档中的严格成功、配对姿态图和测量窗口各有独立定义，不能混成一组当前结果。未能与测量记录对应的图表、完成率、峰值和统一训练参数不进入当前网页正文。

`scripts/generate-research-figures.py` 可从归档 CSV 重绘四组历史100 mm数据图，输出仍写入归档目录，需要Python、numpy、pandas和matplotlib。归档50 mm参考曲线和原始阶段图保留各自出处与限制。

历史PDF保留在归档目录，不作为当前网页的数据入口。当前公开网址未变化，GitHub Pages二维码继续有效。仓库不含托管凭据或私人本机路径。
