# MesenCE 简体中文版

这是 [nesdev-org/MesenCE](https://github.com/nesdev-org/MesenCE) 的个人 fork，加入：

- **运行时语言切换**：跟随系统 / English / 简体中文；
- **简体中文翻译**：界面、设置、常用对话框、快捷键等；
- **AOT 自包含构建**：不依赖系统的 .NET 运行时；
- **本地 PKGBUILD**：在 Arch 系上安装为 `mesen-ce-zh`。

> 本 fork 仅供个人使用与备份，未提交到 AUR。上游目前没有本地化计划，因此 i18n 代码由本 fork 维护。

## 快速开始

```bash
git clone https://github.com/yuzu-1012/MesenCE.git
cd MesenCE
git checkout zh-v4

cd packaging/arch
updpkgsums
makepkg -si

mesen-ce-zh
```

详细说明（依赖、构建、语言切换、外部翻译文件、恢复、同步上游）见 [docs/zh-CN.md](docs/zh-CN.md)。

## 备份与恢复

- 工作分支：`zh-cn`
- 里程碑 tag：`zh-v1`、`zh-v2`……
- 每个 tag 都对应一个可构建的 `PKGBUILD` 版本；
- 换机后 `git clone` + `git checkout <tag>` + `makepkg -si` 即可复原。

## 翻译进度

```bash
python3 tools/localization/xmltool.py stats zh-CN
```

当前进度以该命令输出为准。M1–M3 的界面汉化已完成：主菜单及下拉菜单、设置、视频/音频、各机种配置、输入/控制器配置、调试器、内存查看/搜索、断点、调用栈、标签/注释、图块/精灵/调色板查看器、汇编器/脚本、NES 文件头编辑器、金手指、联机、高清素材包等。剩余未翻译项为专有名词、按键名、分辨率/采样率数值等，运行时保持英文显示。

## 目录

| 路径 | 内容 |
|---|---|
| `UI/Localization/ResourceHelper.cs` | 语言选择、英文底稿、覆盖与回退 |
| `UI/Localization/resources.zh-CN.xml` | 简体中文翻译 |
| `UI/Config/PreferencesConfig.cs` | `MesenLanguage` 枚举与设置项 |
| `UI/Views/PreferencesConfigView.axaml` | 语言下拉框 |
| `tools/localization/` | 翻译校验工具与术语表 |
| `packaging/arch/` | 本地 AOT PKGBUILD 与恢复脚本 |
| `docs/zh-CN.md` | 完整使用说明 |

## 许可

与上游一致，GPL-3.0-or-later。翻译文件同样按 GPL-3.0-or-later 分发。
