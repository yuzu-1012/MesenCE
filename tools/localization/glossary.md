# 简体中文翻译术语表

翻译前先看这里，保证同类文案用词一致。

## 核心术语

| English | 简体中文 | 说明 |
|---|---|---|
| Save State | 即时存档 | 不是“保存状态” |
| Load State | 读取即时存档 | |
| Save Slot | 存档槽 | |
| Fast Forward | 快进 | |
| Rewind | 倒带 | |
| Frame | 帧 | |
| Frame Counter | 帧计数器 | |
| Scanline | 扫描线 | |
| Sprite | 精灵 | |
| BG Layer | 背景层 | |
| Tilemap | 图块地图 | |
| Tile | 图块 | |
| Palette | 调色板 | |
| Cheat | 金手指 | |
| Movie | 录像 | 指输入录像，不是视频文件 |
| Video Recording | 视频录制 | |
| Firmware | 固件 | |
| Overscan | 过扫描 | |
| Breakpoint | 断点 | |
| Watch | 监视 | |
| Trace Logger | 跟踪日志 | |
| Disassembly | 反汇编 | |
| Netplay | 联机 | |
| HD Pack | 高清素材包 | |
| Shader | 着色器 | |
| Aspect Ratio | 宽高比 | |
| Integer Scale | 整数缩放 | |
| Bilinear Interpolation | 双线性插值 | |
| Variable Refresh Rate (VRR) | 可变刷新率 | |
| Run Ahead | 预运行 | |
| Input Display | 输入显示 | |
| HUD | HUD | 保留缩写 |
| Game Selection Screen | 游戏选择画面 | |

## 机种名称

| 保留原文 | 说明 |
|---|---|
| NES / Famicom | NES、红白机（Famicom 可写“红白机”） |
| SNES | SNES |
| Game Boy / GBC / GBA | Game Boy、GBC、GBA |
| PC Engine / PCE | PC Engine、PCE |
| SMS / Game Gear | SMS、Game Gear |
| WonderSwan / WS | WonderSwan、WS |
| ColecoVision | ColecoVision |
| Virtual Boy | Virtual Boy |

## 格式约定

1. 菜单快捷键保留助记符：`_File` → `文件(_F)`。
2. 保留技术专有名词：SDL2、WASAPI、DirectSound、FreeSync、G-Sync、xBRZ、HQ2x、Sinc、Gauss、sRGB。
3. 中文使用全角标点；省略号用 `…`，不用 `...`。
4. 不翻译 XML 的 `ID`、枚举值名、`Form`/`Control` 的 `ID`。
5. 必须原样保留 `{0}`、`{1}` 等占位符及其编号。
6. 多行提示用 `\n` 分段，不要用空格硬凑。
7. 数值单位：`ms` → `毫秒`，`bytes` → `字节`，`fps` 保留。
8. 按钮文案尽量短：`OK` → `确定`，`Cancel` → `取消`，`Reset to Defaults` → `恢复默认值`。

## 修改流程

```bash
# 1. 编辑 UI/Localization/resources.zh-CN.xml
# 2. 校验
python3 tools/localization/xmltool.py check zh-CN
# 3. 看进度
python3 tools/localization/xmltool.py stats zh-CN
# 4. 提交
```

翻译文件必须与 `resources.en.xml` 的 key 完全对应；缺失的 key 运行时会自动回退英文。
