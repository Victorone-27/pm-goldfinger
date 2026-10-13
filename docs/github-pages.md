# GitHub Pages 发布步骤（尚未执行）

当前没有远程仓库，用户已确认网页顶部先显示 **GitHub · 待公开**。本轮只完成静态网页、长图和本地验证，没有创建 GitHub 仓库、推送代码或启用 Pages。下面的操作须在用户确认发布后执行；M7 内容验收通过不自动等于同意发布。

## 当前可发布的内容

- [index.html](index.html)：单文件网页，CSS、交互和四张效果图均内嵌，离线打开即可显示。
- [assets/boss-longimage.png](assets/boss-longimage.png)：1080px 宽的作品集长图，页面顶部“保存作品集长图”指向它。
- `.nojekyll`：发布目录中的空文件，跳过 Jekyll 处理。这个站点不需要 Node、Python 服务或构建框架。
- 图片查看和页内导航均在本地执行，无第三方字体、追踪或脚本请求。作者介绍只用已确认文字，联系方式为“邮箱：待补充”。

## 发布前最后补齐

用户最新确认的发布流程分四个阶段，每阶段交验收后暂停：

1. **本地安全审查。** 检查工作区和全部 Git 历史。历史发现密钥立即停止；不改写历史、不强制推送。当前文件的路径、忽略规则与许可可先修正，历史个人信息和旧截图的处理方式必须由用户决定。不得自行改用无历史的新仓库绕过问题。
2. **网页建仓库。** 仅在用户已登录 Chrome 的 `github.com` 新标签操作；先展示登录用户名，等确认后创建公开 `pm-goldfinger`，不添加远程 README、忽略文件或许可。不读取其他标签或修改账号设置。
3. **推送和启用 Pages。** 按用户要求运行 `gh auth login --web`，授权页面由用户本人点击。授权后关联已确认的仓库，提交获准的本地改动并推送 `main`；Pages 选择 `main` 的 `/docs`，部署后检查网页、图片和链接。提交身份须先确认，不沿用含本机主机名的自动邮箱。
4. **补齐真实链接。** 将 README、网页、长图和一屏卡中的仓库与 Pages 占位替换为已验证的地址；一屏卡加入 Pages 二维码，重导图片后提交、推送并交最终报告。联系方式继续保持“邮箱：待补充”。

用户已明确选择 A，授权清理上述历史后重新审查。历史清理已完成，原始历史只在仓库外私有备份；[清理说明](history-sanitization.md)记录范围。当前停在阶段 1 的复审验收，等待用户确认后才进入建仓库阶段。任何步骤出错或与预期不符，停止告知用户。

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
