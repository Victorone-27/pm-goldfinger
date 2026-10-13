# GitHub Pages 发布记录

发布日期：2026-10-14。

项目已发布到公开仓库：[Victorone-27/pm-goldfinger](https://github.com/Victorone-27/pm-goldfinger)。GitHub Pages 使用 `main` 分支的 `/docs` 目录，线上地址为 [https://victorone-27.github.io/pm-goldfinger/](https://victorone-27.github.io/pm-goldfinger/)。

## 已完成的发布检查

- Git 历史保留 13 次里程碑提交，作者与提交者邮箱已统一为经账号核对的公开邮箱；发布前安全修正另有一条提交。
- 仓库没有强制推送；当前 `main` 与远程一致，未发布本地运行目录、浏览器 profile、缓存、日志或密钥。
- Pages 来源已配置为 `main` + `/docs`，部署状态为 `built`。
- 线上首页返回 HTTP 200；首页内嵌的 4 张图片、页面链接和作品集下载资源均检查通过。
- 作品集顶部链接指向公开仓库，底部提供 Pages 链接和二维码；联系方式仍为“邮箱：待补充”。

## 文件入口

- [作品集网页](index.html)
- [BOSS 作品集长图](assets/boss-longimage.png)
- [手机宽度预览](assets/boss-phone-preview.png)
- [桌面网页预览](assets/portfolio-desktop.png)
- [手机网页预览](assets/portfolio-mobile.png)

## 后续维护

更新 `docs/` 下的网页或素材后，提交并推送 `main`，Pages 会自动重新构建。若改动了网页布局，应重新导出长图与手机宽度预览，并检查二维码仍指向上述 Pages 地址。
