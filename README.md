# Freebird 曲线编辑插件

面向 [Freebird XR](https://freebirdxr.com/) 的 Blender/VR 曲线编辑插件。当前仓库处于开发准备阶段，尚未包含插件功能代码。

## 开发基准

- 操作系统：Windows
- Blender：`3.6.23 LTS`
- Blender 可执行文件：`C:\blender\software\stable\blender-3.6.23-lts.e467db79ca8c\blender.exe`
- Freebird XR：本机当前安装版本 `2.14.2`，提交 `dd3cb84`
- Freebird 安装目录：`%APPDATA%\Blender Foundation\Blender\3.6\scripts\addons\freebird_xr`

后续开发与验证均以此组合为主基准。Freebird 更新后，应先记录新版本和提交号，再进行兼容性验证。

## 技术背景

根据 [Freebird 插件文档](https://freebirdxr.com/docs/plugins/)：

- 插件可以是单个 Python 文件，也可以是带 `__init__.py` 的 Python 包；
- Windows 默认插件目录为 `%USERPROFILE%\.freebird\plugins`；
- 顶层入口必须定义含 `name` 字段的 `fb_info`；
- `register()` 与 `unregister()` 为可选生命周期函数；
- 可通过 `freebird.api` 注册主菜单入口，通过 `freebird.utils.log` 写入 Freebird 日志。

曲线编辑器预计采用包结构，按注册、界面、曲线操作和状态管理拆分模块，避免将功能集中在单一文件中。实际目录和 API 设计将在功能需求确认后落地。

## 仓库约定

- 默认分支：`main`
- Python、Markdown 和配置文件：UTF-8（无 BOM）、LF
- PowerShell、CMD 和批处理文件：UTF-8（无 BOM）、CRLF
- 本地 Freebird 数据、Python 缓存、虚拟环境及 Blender 自动备份文件不进入版本库
- 每次修改同步更新 `PROJECT.md`

## 本地安装位置

后续开发出的插件包将放入或链接到：

```text
C:\Users\<用户名>\.freebird\plugins\
```

可在 Blender 的 `Freebird Settings` 中使用 `Open Plugins Folder` 打开目录，并通过 `Reload All` 重新加载插件。
