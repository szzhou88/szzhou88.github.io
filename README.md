# Sizhuo Zhou · Academic Homepage

个人学术主页，使用静态 HTML/CSS/JavaScript 和 Python 标准库生成，无需安装第三方依赖。

目标网址：https://szzhou88.github.io/

## 日常更新

可以直接在 GitHub 仓库中打开相应文件，点击铅笔图标修改，再点击 **Commit changes** 提交到 `main`。GitHub Actions 会自动重新生成并发布网站。请在 **Actions → Deploy academic homepage** 查看运行结果；绿色勾号表示发布完成。

| 要修改的内容 | 文件 |
| --- | --- |
| 个人简介、导师、荣誉、研究兴趣、联系方式、审稿服务 | `template.html` |
| 论文标题、作者、会议、链接、配图 | `publications.json` |
| News 的接收月份、会议名称、篇数 | `news.json` |
| 照片 | `assets/portrait.jpg` |
| 论文图片 | `assets/papers/` |
| 字号、间距、配色、响应式排版 | `style.css` |

**不要只修改 `index.html`**：它是生成文件，自动部署时会被 `template.html` 和两个 JSON 文件重新生成。JSON 文件使用英文双引号，各条记录之间用逗号分隔，最后一条记录后不加逗号。

## 新增论文和 News

1. 在 `assets/papers/` 上传论文代表图。建议使用清晰的 PNG/JPG；只上传准备公开的图片。
2. 在 `news.json` 添加对应接收事件。例如：

```json
{
  "id": "news-example-2027",
  "date": "2027-01",
  "count": 1,
  "venue": "Example Conference 2027",
  "kind": "accepted"
}
```

`date` 是接收月份，格式为 `YYYY-MM`。若只能确认发表时间，可将 `kind` 设为 `published`。同一会议同一批次有多篇文章时，复用该事件并更新 `count`。

3. 在 `publications.json` 复制一条现有论文记录并修改。每篇 `id` 必须唯一，`newsKey` 必须与 News 中的 `id` 相同。例如：

```json
{
  "id": "paper-11",
  "title": "Paper title",
  "authors": ["Sizhuo Zhou", "Coauthor Name"],
  "venue": "Example Conference",
  "year": 2027,
  "track": "Main Conference",
  "publicationStatus": "published",
  "newsKey": "news-example-2027",
  "url": "https://arxiv.org/abs/XXXX.XXXXX",
  "linkLabel": "Paper",
  "image": "assets/papers/example.png",
  "imageAlt": "Overview of the proposed method",
  "imageSize": [1200, 600],
  "imageCrop": [0, 0, 1200, 600]
}
```

- `imageSize`：原图真实宽、高（像素）。
- `imageCrop`：预览裁剪范围 `[左边距, 顶边距, 宽度, 高度]`。范围不能超出原图。点击预览仍可查看原图。
- 尚未公开的论文：`publicationStatus` 用 `forthcoming`，`url` 和 `linkLabel` 可为空字符串；公开后更新状态和链接。
- 可用 `venueLabel` 自定义显示名称，例如 `"IEEE TVCG"`。
- 论文和 News 都按事件时间从新到旧自动排序，无须手动排列。论文显示日期来自 `newsKey` 对应的 News；只改 `publicationDate` 不会修改页面接收日期。
- 既有 News 日期包含先前提供的日期及会议通知月份；如收到更准确的接收时间，直接修改 `news.json` 中对应月份。
- `publications-source.md` 只是初始资料备份，日常维护以 `publications.json` 为准，不需要运行 `--import`。

## 本地预览

在项目文件夹中执行：

```bash
python3 build.py
python3 -m http.server 8765 --bind 127.0.0.1
```

浏览器打开 http://127.0.0.1:8765/ 。修改后再次运行 `python3 build.py` 并刷新页面；停止预览按 `Ctrl+C`。

部署打包检查：

```bash
python3 build.py --output _site
```

`_site/` 只包含网页、样式、脚本和实际使用的图片，不包含源 PDF、临时文件或维护文档。`tmp/` 和 `_site/` 均不提交到 Git。

## 首次部署设置

仓库名称必须为 `szzhou88.github.io`，使用公开仓库。在 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。提交到 `main` 后，`.github/workflows/pages.yml` 自动构建和部署。也可在 Actions 中手动点击 **Run workflow**。

官方说明：https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

## 排查与回退

- 页面没变化：先等 Actions 运行完成，再用 `Command+Shift+R` 强制刷新；GitHub Pages 更新可能需要几分钟。
- Actions 显示失败：点击失败的运行 → build → Build static website 查看错误，优先检查 JSON 语法、`newsKey`、图片路径及裁剪范围。
- 想撤回修改：在 GitHub 文件的 History 找到修改前版本，将旧内容复制回文件并提交；也可以让我根据具体提交恢复。
- 更换不同尺寸的照片：同步调整 `style.css` 中 `.portrait` 的尺寸与裁剪样式，检查电脑和手机显示。
- 请勿把未准备公开的完整稿件、账号凭据或私人文件上传到公开仓库。论文图片来源记录位于 `assets/papers/sources.json`。
