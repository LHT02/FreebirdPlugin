# Freebird 曲线编辑插件

面向 [Freebird XR](https://freebirdxr.com/) 的 Blender/VR 曲线编辑增强插件。

## 开发基准

- 操作系统：Windows
- Blender：`3.6.23 LTS`
- Blender 可执行文件：`C:\blender\software\stable\blender-3.6.23-lts.e467db79ca8c\blender.exe`
- Freebird XR：本机当前安装版本 `2.14.2`，提交 `dd3cb84`
- Freebird 安装目录：`%APPDATA%\Blender Foundation\Blender\3.6\scripts\addons\freebird_xr`

后续开发与验证均以此组合为主基准。Freebird 更新后，应先记录新版本和提交号，再进行兼容性验证。

## 当前功能

- 编辑一个 Curve 对象中的全部 spline，不再局限于 `splines[0]`。
- 抓住节点移动时，旋转实体 VR 控制器可修改节点 `tilt`；不会新增或占用旋转环。每次抓取会锁定初始切线，并过滤四元数符号翻转和追踪跳变，避免垂直、内收曲线出现突然扭转。
- 抓住节点移动时，主手摇杆上下缩放节点 `radius`。
- 支持可开关的衰减编辑；移动、扭转和半径变化均按衰减权重影响邻近节点。
- 在 `CUSTOM` 菜单切换到 `DRAW IN` 后，复用 Freebird 笔画采样逻辑，在当前 Curve 对象中新增 spline。
- 新增 spline 的节点半径可通过 `RADIUS -`、`RADIUS +` 设置。
- 支持 NURBS、POLY，并适配 Bézier 控制点的选择、移动、扭转和半径。
- `CUSTOM` 页面中的绘制、编辑、衰减和半径按钮均带有插件自带图标。

## VR 操作

1. 选择 Curve 对象并进入编辑模式。
2. 打开 Freebird 主菜单的 `CUSTOM` 页面。
3. 使用 `EDIT` 返回增强编辑模式；使用 `DRAW IN` 在当前对象中连续绘制新 spline。
4. 编辑节点时直接抓住并拖动：
   - 移动控制器改变位置；
   - 转动手腕改变曲线扭转；
   - 推动主手摇杆上下改变节点半径。
5. 使用 `FALLOFF ON/OFF` 切换衰减编辑。抓取前，Freebird 原有的摇杆比例范围调节仍然有效；开始抓取后，主手摇杆优先控制节点半径。

绘制半径显示为节点 `radius` 倍率。开启 Freebird 的 `Fixed Thickness` 时整根新 spline 使用该倍率；未开启时，控制器压力会与该倍率相乘。

## 开发安装

使用 PowerShell 7：

```powershell
pwsh -NoProfile -File .\tools\install-dev.ps1
```

脚本只会在目标不存在时创建开发目录联接，不会覆盖现有插件。安装后，在确认当前 Blender 工作可以安全重载时，使用 `Freebird Settings > Reload All`。

完整检查：

```powershell
pwsh -NoProfile -File .\tools\verify.ps1
```

## 技术背景

根据 [Freebird 插件文档](https://freebirdxr.com/docs/plugins/)：

- 插件可以是单个 Python 文件，也可以是带 `__init__.py` 的 Python 包；
- Windows 默认插件目录为 `%USERPROFILE%\.freebird\plugins`；
- 顶层入口必须定义含 `name` 字段的 `fb_info`；
- `register()` 与 `unregister()` 为可选生命周期函数；
- 可通过 `freebird.api` 注册主菜单入口，通过 `freebird.utils.log` 写入 Freebird 日志。

插件采用包结构，按生命周期、兼容补丁、曲线数据访问、绘制、交互和命令拆分模块。

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
