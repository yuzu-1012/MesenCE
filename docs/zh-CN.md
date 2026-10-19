# MesenCE 简体中文版：构建、安装与恢复

这个 fork 在 [nesdev-org/MesenCE](https://github.com/nesdev-org/MesenCE) 的基础上加入了运行时可切换的本地化支持，并附带简体中文翻译。

- 上游版本：`2.2.1-99-g4b8a196e`（`net10.0`）
- 本地化：`Auto` / `English` / `简体中文`
- 构建：AOT 自包含，不依赖系统的 `dotnet-runtime`
- 打包：本地 PKGBUILD，安装为 `mesen-ce-zh`

## 1. 安装依赖

```bash
sudo pacman -S --needed \
  base-devel clang dotnet-sdk-10.0 pkgconf zlib binutils \
  sdl2 libevdev fontconfig glib2 \
  libx11 libxcursor libxext libxi libxrandr libglvnd icu
```

中文字体不是硬依赖；如果界面出现方框，安装 `noto-fonts-cjk`。

## 2. 从 tag 构建并安装（推荐）

> 说明：源码 tag 里也包含这个 `PKGBUILD`，所以 tag 内的 `sha256sums` 只能是 `SKIP`（tarball 的校验和无法写进 tarball 自身）。checkout tag 后先运行 `updpkgsums` 生成校验和；`zh-cn` 分支上的 PKGBUILD 已经记录了 `zh-v1` 的校验和。

先确保对应的 tag 已经推送到 GitHub：

```bash
git ls-remote --tags origin 'zh-v*'
```

然后：

```bash
cd packaging/arch
updpkgsums          # 首次使用或 tag 更新后执行
makepkg -si
```

安装后：

```bash
mesen-ce-zh
```

卸载：

```bash
sudo pacman -Rns mesen-ce-zh
```

用户数据（设置、存档、解压出的 `MesenCore.so` 等）在 `~/.config/MesenCE`，卸载包不会删除。

## 3. 不依赖 GitHub tag 的构建

如果 tag 还没推送，或想直接验证当前 checkout：

```bash
./packaging/arch/build-from-checkout.sh
./packaging/arch/build-output/mesen-ce-zh
```

脚本会把当前 `HEAD` 导出到临时目录后构建，不会污染工作区。注意：它只包含**已提交**的改动，未提交的修改请先 commit。

也可以直接在主目录构建：

```bash
make USE_AOT=true LTO=true STATICLINK=false SYSTEM_LIBEVDEV=true
./bin/linux-x64/Release/linux-x64/publish/Mesen
```

这会在仓库里留下 `bin/`、`obj.*` 等构建产物（已被 `.gitignore` 忽略）。

## 4. 切换语言

启动后进入 **设置 → 首选项 → 常规 → 显示语言**：

- **跟随系统**：`LANG=zh_CN.UTF-8` 时自动使用简体中文，其他语言环境回退英文；
- **English**：强制英文；
- **简体中文**：强制中文。

语言切换需要重启 Mesen 生效。

## 5. 不重新编译就修改翻译

运行时优先读取外部翻译文件：

```
~/.config/MesenCE/Localization/resources.zh-CN.xml
```

把 `UI/Localization/resources.zh-CN.xml` 复制到该路径，修改后重启 Mesen 即可看到效果。删除该文件就回到内嵌翻译。

## 6. 翻译工作流

```bash
python3 tools/localization/xmltool.py stats zh-CN
python3 tools/localization/xmltool.py check zh-CN
python3 tools/localization/xmltool.py merge zh-CN
```

- `stats`：查看翻译进度；
- `check`：校验 key、占位符和 XML 格式，提交前必须通过；
- `merge`：上游新增 key 后，把英文条目补进中文文件。

术语和格式约定见 [`tools/localization/glossary.md`](../tools/localization/glossary.md)。

## 7. 从 GitHub 恢复

```bash
git clone https://github.com/yuzu-1012/MesenCE.git
cd MesenCE
git checkout zh-v1
cd packaging/arch
updpkgsums
makepkg -si
```

每个里程碑对应一个 tag（`zh-v1`、`zh-v2`……），`PKGBUILD` 里的 `_tag`/`pkgver` 会同步更新。

## 8. 同步上游

```bash
git fetch upstream
git checkout zh-cn
git rebase upstream/master
# 解决冲突后：
python3 tools/localization/xmltool.py merge zh-CN
python3 tools/localization/xmltool.py check zh-CN
git push --force-with-lease origin zh-cn
```

上游可能改动 `resources.en.xml`；`merge` 会把新增 key 以英文补进中文文件，未翻译的 key 运行时会自动回退英文。

## 9. 已知限制

- 目前只有简体中文（`zh-CN`）；繁体中文会回退英文，未来可加 `resources.zh-TW.xml`。
- 调试器文档 JSON、部分 XAML 字面量和 C++ 日志仍是英文，属于后续里程碑。
- `librashader` 着色器支持需要额外的 `librashader.so`，本仓库默认不包含。
