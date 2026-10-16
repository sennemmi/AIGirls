# ZipZipPipe 视觉资产与 Logo 核验

更新时间：2026-10-16。十位核心角色已从原作者两批画廊逐张对照识别。

## 十位标准立绘对应

| 角色 | 原帖 | 图序 | 资源目录 |
|---|---|---:|---|
| deepseek | [B站动态](https://www.bilibili.com/opus/1233069202138464289) | 1 | characters/deepseek/ |
| kimi | [B站动态](https://www.bilibili.com/opus/1233069202138464289) | 2 | characters/kimi/ |
| glm | [B站动态](https://www.bilibili.com/opus/1233069202138464289) | 3 | characters/glm/ |
| qwen | [B站动态](https://www.bilibili.com/opus/1233069202138464289) | 4 | characters/qwen/ |
| gemini | [B站动态](https://www.bilibili.com/opus/1233069202138464289) | 5 | characters/gemini/ |
| claude | [B站动态](https://www.bilibili.com/opus/1233069202138464289) | 6 | characters/claude/ |
| gpt | [B站动态](https://www.bilibili.com/opus/1233069202138464289) | 7 | characters/gpt/ |
| grok | [B站动态](https://www.bilibili.com/opus/1233069202138464289) | 8 | characters/grok/ |
| doubao | [B站动态](https://www.bilibili.com/opus/1236803362705375305) | 1 | characters/doubao/ |
| minimax | [B站动态](https://www.bilibili.com/opus/1236803362705375305) | 5 | characters/minimax/ |

## 文件结构

每位 AI 使用 characters/{角色名}/ 文件夹：logo.svg 为品牌标志 SVG 参考、SOURCE.md 记录图片和 Logo 原始来源，portrait.png 或 portrait.jpg 为自动导入且通过全套尺寸校验的 ZipZipPipe 原始美术文件。
人物的现有 Markdown 档案继续位于 characters/{角色名}.md；每个资源目录 SOURCE.md 已链接到对应人设。

## 下载状态及核验

资源目录和 Logo 已提交。十幅立绘通过 scripts/import_zipzippipe_art.py 在 PR #2 的 GitHub Actions 中整批获取；只有 10/10 均成功且每幅短边不少于 700 像素才写入并提交。
是否导入完成要查看 data/artwork-verification.json 的 SHA256 / 尺寸记录及实际 portrait 文件；没有这些文件就代表未完成，绝不能声称已经上传原画。

## 版权与商标

ZipZipPipe 两条动态均有置顶说明：DeepSeek 鲸鱼娘基于上善无形的原创，依 CC BY-NC-SA 4.0 非商业与相同方式共享协议二创。
这不自动证明所有其余形象均具有完全相同授权。公开发布、评论区所称开源不能替代逐图许可；将来商用请与相关权利人确认。
SVG 参考图源自 LobeHub/lobe-icons 社区图标资源（MIT 实现），并非所有品牌方直接发布的官方授权素材；商标权保留给原权利人。仓库 MIT LICENSE 不覆盖第三方艺术作品和商标。
