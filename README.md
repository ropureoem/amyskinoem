# amyskinoem

Amy Skin OEM —— 中国私牌护肤品生产商。低 MOQ 1000、12 个现成配方与定制配方。GitHub Pages 原型站（2026-11-06 上线，框架依据 Issue #1）。

- 线上地址：https://tileserachied.github.io/amyskinoem/
- 目标域名：[amyskinoem.com](https://amyskinoem.com/)（已注册；DNS 尚未解析，见 M11。先不要加 CNAME——已实测：加 CNAME 会导致 GitHub Pages 把线上站重定向到无法解析的域名；CNAME 已删除，等 DNS 生效后再加。所有 canonical 与 sitemap 已指向 amyskinoem.com）
- 联系：WhatsApp https://wa.me/8618928823858 · info@amyskinoem.com
- Logo：已定 E（Sans Caps，大写 AMY SKIN，字母间距）。完整 VI 见 brand.html 与套件页 brand-kit.html（见下文「VI 标准套件」）：颜色 Ink #1A1A1A、Charcoal #333333、Warm Grey #8A8378、Ivory #FAF8F5，字体 Arial / Helvetica，留白 1x cap-A，最小尺寸 20 mm 印刷 / 100 px 屏幕，单色与反白版本、面膜袋与管状包装用的窄距版本，以及各类产品效果图。方向 D（Serif 衬线标志）未被选中；堆叠版作为方形场景变体，已收录于 VI 套件（见下文）。方向 A/B/C（花瓣、植物、拱形）与早期现代水滴标志已被否决并删除。
- 规则：只写配方（无型号），每 SKU 起订量 1000，无固定价、按单私下报价，只做获客；广州合作工厂，不写“自有工厂 / 投资工厂”；唯一可证实的认证是 SGS ISO 22716（Sanmusheng），Moksha / Wangsha 的认证待核实；产品图为临时视觉（见下文「图片」）：Moksha 官网图片热链引用，原品牌标签以 Amy Skin 标签贴片盖住；工厂/实验室图画面无厂名，原样使用、不加 Amy Skin 标志；文字上不写自有工厂、不声称照片是自家工厂。真实产品照片待拍摄（M7）。

## 本次原型已建成

- 首页 index.html：S0–S11（Hero、6 分类、12 配方预览、品牌、MOQ 1000、按市场分的认证、质量与打样、5 步 OEM/ODM 流程、配方知识、关于/工厂、博客预览、底部 CTA）+ 常见问题（GEO）。
- 分类页 categories.html（6 分类、12 配方总表）、流程 process.html（HowTo 结构化数据）、包装 packaging.html、认证 certifications.html、关于 about.html（内含 M1–M11 清单）、询价 quote.html（mailto 表单 + WhatsApp）、博客索引 blog.html。
- 12 个配方页 formulas/：Vitamin C、Hyaluronic Acid、Niacinamide、Peptide 精华，Moisturising、Anti-Aging 面霜，Amino Acid 洁面，Hydrating 爽肤水，Sheet Mask，Body Lotion，Shampoo，Sunscreen SPF50。每页含 FAQPage 结构化数据。
- 6 篇 GEO 博客 blog/：选精华配方、Vitamin C 对比 Niacinamide、MOQ 1000 的含义、打样流程、包装方案、ISO 22716 的含义。每篇先给直接答案，再展开，含 FAQPage 结构化数据。
- SEO / GEO：每页独立 title/meta/canonical；首页含 12 个种子关键词；Organization 与 FAQPage 结构化数据；sitemap.xml 仅含 28 个英文 URL（含 brand.html 与 brand-kit.html）；中文页 zh/index.html 占位，noindex/nofollow，robots.txt 屏蔽 /zh/，不进 sitemap。

## 仍缺资料（Issue #1 事项 M1–M11）

- M1 公司资料：公司简介、时间线、与工厂的确切关系、工厂地址、产线与产能——本站不编造任何工厂数字与产能。
- M2 证书：Sanmusheng 的 SGS ISO 22716 证书编号与范围。
- M3 各市场认证范围：CPSR / PIF / CPNP / SCPN、FDA / MoCRA 等，按单确认。
- M4 包装供应商：具体包装系列、尺寸与起订量。
- M5 打样：样品费、打样周期、修改次数。
- M6 交期与付款：大货交期、付款条款、各步骤时间。
- M7 产品图：带 Amy Skin E logo 的真实产品图与工厂图（临时视觉见下文「图片」；真实照片待拍摄）。
- M8 信任素材：展会、展厅或荣誉（如有）。
- M9 联系方式：WhatsApp 与邮箱已确认；Instagram / TikTok 等社交渠道待确认（头像与横幅文件已备好，见下文「VI 标准套件」）。
- M10 中文文案：完整中文落地页文案待提供；现有 zh/index.html 仅为占位页。
- M11 域名：amyskinoem.com 已注册但 DNS 尚未解析；注册商处完成解析后，重新在仓库加 CNAME（内容为 amyskinoem.com）或在 Settings > Pages 中设置自定义域名。

## 12 个种子关键词

private label skincare manufacturer、skincare OEM manufacturer China、private label skincare manufacturer China、skincare ODM manufacturer、custom skincare manufacturer low MOQ、private label serum manufacturer、private label cream manufacturer、private label facial mask manufacturer、OEM skincare manufacturer Guangzhou、private label sunscreen manufacturer、custom skincare formulation China、skincare private label MOQ 1000。

## 图片（临时视觉）

- 13 张图片全部取自 Moksha 官网（moksha-bio.com），以原链接热链引用，未存入仓库；Sanmusheng 未找到官网/画册，未用其图片。
- 产品图：CSS 裁剪到产品区 + 白色 Amy Skin 标签贴片（内含 logo-e.svg）整块盖住原品牌标签，画面中不得出现 SADOER、BIOAQUA、FAYANKOU、ZOU、JENSY、MOKSHA 等原品牌字样；迪拜展会横幅裁去两侧文字块与认证圆标；防晒图原标 SPF 60 与本站 SPF50 不符，已整块盖住。
- 工厂/实验室图：画面无厂名，原样使用，不加 Amy Skin 标志；文字上不写“自有工厂”，不声称照片是自家工厂。
- 部署：首页 Hero、6 个分类卡、12 个配方页、6 篇博客文章与 blog.html、about、packaging、process 均已配图，无空白纯文字区块。
- 上传通道：浏览器下载的文件不能作为本任务文件上传（2026-11-06 裁决），图片只能热链、不能存入仓库；若 Moksha 删除或改名图片，站内对应图片会失效，需替换。真实 Amy Skin 品牌照片拍摄后替换（M7）。
- 13 个热链 URL：
  - Hero / 包装页：https://www.moksha-bio.com/wp-content/uploads/2026/09/Dubai-Exhibition-Carousel-Images-b.webp
  - MOQ 卡：https://www.moksha-bio.com/wp-content/uploads/2026/09/Dubai-Exhibition-Carousel-Images-c.webp
  - 面霜罐：https://www.moksha-bio.com/wp-content/uploads/2024/10/%E9%9D%A2%E9%9C%9C800x500.png
  - 烟酰胺精华：https://www.moksha-bio.com/wp-content/uploads/2026/11/niacinamide-spot-serum-oem-1.webp
  - 胡萝卜精华：https://www.moksha-bio.com/wp-content/uploads/2026/11/carrot-face-serum-oem-1.webp
  - 维 E 蜂蜜精华：https://www.moksha-bio.com/wp-content/uploads/2026/11/vitamin-e-honey-serum-oem-1.webp
  - 积雪草爽肤水：https://www.moksha-bio.com/wp-content/uploads/2026/11/centella-asiatica-face-toner-oem-1.webp
  - 维 C 氨基酸洁面：https://www.moksha-bio.com/wp-content/uploads/2026/10/feat1029b_cleanser.webp
  - 防晒霜：https://www.moksha-bio.com/wp-content/uploads/2026/11/spf-60-sunscreen-cream-oem-1.webp
  - 洋甘菊面膜：https://www.moksha-bio.com/wp-content/uploads/2026/11/chamomile-facial-mask-oem-1.webp
  - 角蛋白洗发水：https://www.moksha-bio.com/wp-content/uploads/2026/10/keratin-shampoo-conditioner-set-1.jpg
  - 车间流水线：https://www.moksha-bio.com/wp-content/uploads/2024/10/2021-08-18-221443-1-scaled.jpg
  - 实验室：https://www.moksha-bio.com/wp-content/uploads/2024/10/2021-08-19-182615-1-scaled.jpg

## VI 标准套件

- 套件页：brand-kit.html（已进 sitemap.xml；brand.html 页脚已链接到套件页）。
- 11 个文件，全部在 assets/brand/，均为 SVG 矢量原稿：logo-main.svg（主标，墨字白底）、logo-reverse.svg（反白，白字墨底）、logo-narrow.svg（窄版，tracking 6）、logo-stacked.svg（堆叠版）、avatar.svg（社交头像 1080×1080，墨底白标）、banner.svg（社交横幅 1600×900，Ivory 底，AMY SKIN + SKINCARE OEM）、whatsapp.svg（WhatsApp 商家头像 1080×1080，白底墨标）、mockup-serum.svg（精华瓶标签样机）、mockup-cream.svg（面霜罐标签样机）、mockup-mask.svg（面膜袋标签样机）、vi-sheet.svg（一页 VI 标准单，A4 纵向：六色色板、字体、留白、最小尺寸、Do / Don't）。
- 三个标签样机为 SVG 内嵌 Moksha 产品图热链 + 白色 Amy Skin 标签；套件页用 `<object>` 嵌入预览（用 `<img>` 时浏览器沙箱不加载内嵌的外部图片）。
- 说明：社交平台上传头像一般不接受 SVG，需自行导出 JPG/PNG（头像 1080×1080，横幅 1600×900）；VI 单以 SVG 交付，无 PDF（无二进制上传通道）。
