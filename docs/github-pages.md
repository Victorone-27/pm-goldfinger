# GitHub Pages 发布步骤（尚未执行）

当前没有远程仓库，用户已确认网页顶部先显示 **GitHub · 待公开**。本轮只完成静态网页、长图和本地验证，没有创建 GitHub 仓库、推送代码或启用 Pages。下面的操作须在用户确认发布后执行；M7 内容验收通过不自动等于同意发布。

## 当前可发布的内容

- [index.html](index.html)：单文件网页，CSS、交互和四张效果图均内嵌，离线打开即可显示。
- [assets/boss-longimage.png](assets/boss-longimage.png)：1080px 宽的作品集长图，页面顶部“保存作品集长图”指向它。
- `.nojekyll`：发布目录中的空文件，跳过 Jekyll 处理。这个站点不需要 Node、Python 服务或构建框架。
- 图片查看和页内导航均在本地执行，无第三方字体、追踪或脚本请求。作者介绍只用已确认文字，联系方式为“邮箱：待补充”。

## 发布前最后补齐

1. 由用户确定 GitHub 仓库地址与可见性。将 `index.html` 顶部 `.repo` 的占位元素替换为指向该仓库的真实链接，再同步导出长图。当前没有虚构用户名、仓库地址或站点 URL。
2. 以 **M7 净文件交付包**建立发布仓库，保留目录结构和 MIT 许可。该包不含 `.git` 历史、`.local`、虚拟环境、密钥或真实运行数据；旧仓库历史仍有未标注原图和本机路径，因此本步骤不直接推送历史提交。若要保留历史，需另行完成历史素材与隐私处理。
3. 用户确认这个具体版本和发布范围后，再创建 / 更新远程仓库并推送。发布本身可能公开整个所选仓库的文件；本步骤不把“网页验收”当作“仓库公开”授权。

## 在 GitHub 中启用

以下路径依据 2026-10-13 实际读取的官方文档：

1. 将确认过的文件放入仓库 `main` 分支，确保 `docs/index.html` 与 `docs/.nojekyll` 在位。
2. 仓库 **Settings → Pages → Build and deployment**。
3. **Source** 选择 **Deploy from a branch**。
4. **Branch** 选择 `main`，目录选择 `/docs`，然后 **Save**。保存会启动实际发布。
5. 等待 Pages 部署成功，从 Pages 设置或部署记录取得真实站点 URL。项目站通常位于 `https://<owner>.github.io/<repository>/`，这里的两个字段是占位，不能当作已发布地址。

普通项目仓库建议保持仓库名与路径一致。这里所有页面内资源 / 下载链接都使用相对路径，已在带 `/pm-goldfinger/` 前缀的本地服务器验证，不依赖网站根路径。

## 发布后核对

- 手机与电脑打开首页，四张效果图加载完整。
- 每张图能打开原尺寸、滑动查看、关闭返回；页内导航正常。
- 长图下载正常，PNG 宽度为 1080px。
- GitHub 入口指向正确仓库；作者介绍、邮箱占位与确认版本一致。
- 页面没有素材加载错误；没有未经确认的第三方请求。

M7 本轮完成的是本地静态验证；线上域名、GitHub 权限和平台部署结果需实际发布后检查。

## 官方依据

- [配置发布来源：分支及 /docs 目录](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [创建 Pages 站点：静态文件及 .nojekyll](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
