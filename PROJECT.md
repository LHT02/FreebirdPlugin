# PROJECT

## 项目目标

开发 Freebird XR 的曲线编辑插件，为 Blender/VR 工作流提供直观的曲线创建与编辑能力。

## 开发原则

- 使用 Python 和 Freebird/Blender 提供的插件接口。
- 按职责拆分注册、UI、曲线操作和状态管理，避免上帝文件。
- Windows 自动化命令使用 PowerShell 7。
- 文本统一保存为 UTF-8（无 BOM）。
- 每次修改记录实现内容、验证结果和未完成事项。

## 固定开发基准

- Blender：`3.6.23 LTS`
- Blender 路径：`C:\blender\software\stable\blender-3.6.23-lts.e467db79ca8c\blender.exe`
- Freebird XR：本机当前安装版本 `2.14.2`，提交 `dd3cb84`
- Freebird 路径：`C:\Users\LHT02\AppData\Roaming\Blender Foundation\Blender\3.6\scripts\addons\freebird_xr`
- Freebird 官方变更日志当前处于 `2.14` 系列；开发时以本机实际安装的 `version.json` 为精确版本依据。

## 变更记录

### 2026-09-03：Git 仓库准备

完成内容：

- 确认工作目录初始为空且尚未初始化 Git。
- 查阅 Freebird 官方插件文档，确认插件是由 Freebird/Blender 加载的 Python 文件或包。
- 准备 `main` 分支的 Git 仓库基线。
- 新增 Python、Blender、Freebird 本地数据和常见编辑器文件的忽略规则。
- 新增换行符、UTF-8（无 BOM）及基本编辑格式约定。
- 新增项目说明与持续维护约定。
- 固定 Blender `3.6.23 LTS` 与本机 Freebird XR `2.14.2`（`dd3cb84`）为首个开发基准。

核验结果：

- 指定的 `blender.exe` 路径存在。
- 检测到该 Blender 当前已有运行实例，因此未启动新的后台实例，避免影响未保存工作。
- 用户级 Blender `3.6` 插件目录中存在 `freebird_xr`。
- `freebird_xr/version.json` 与入口 `bl_info` 均标记版本 `2.14.2`。
- 仓库文本文件已检查为 UTF-8 无 BOM，Git 属性固定普通文本为 LF、Windows 脚本为 CRLF。
- 首次提交前已通过 `git diff --cached --check` 检查。

当前状态：

- 尚未添加曲线编辑功能代码。
- 尚未配置远程仓库。
- 尚未在 Blender/Freebird 中执行插件加载测试。

下一步：

- 确认曲线编辑器的首版功能范围和交互流程。
- 建立 Freebird 插件包骨架及最小加载验证。
- 增加适用于纯 Python 逻辑的自动化测试，并记录 Blender/VR 实机验证结果。

### 2026-09-03：曲线编辑增强插件首版

实现内容：

- 新增 `freebird_curve_editor` Freebird 插件包，并通过版本保护限定 Freebird `2.14.2 / dd3cb84`。
- 将曲线碰撞检测、选择、选择状态、移动目标、擦除和事件目标校验扩展到一个 Curve 数据块中的全部 spline。
- 抓住曲线节点时，把实体控制器绕节点曲线切线的旋转分量映射到 `tilt`；没有新增旋转环，现有变换手柄拖动也不会触发该功能。
- 抓住曲线节点时，使用主手纵向摇杆按指数倍率缩放 `radius`，并在该上下文阻止 Walk 导航和比例范围处理争抢输入。
- 增加衰减编辑开关；依据 Blender 比例编辑半径、连接模式和衰减类型，对位置、扭转和半径统一施加权重。
- 将 Freebird 原有比例编辑范围球扩展到曲线编辑模式，便于在 VR 中观察衰减范围。
- 自动关键帧开启时，为直接编辑的曲线节点补充 `tilt`、`radius` 和 Bézier 手柄关键帧。
- 增加 `DRAW IN`/`EDIT` 模式切换，复用 Freebird NURBS 笔画采样与收尾逻辑，将新 spline 写入当前 Curve 对象。
- 增加新 spline 半径倍率的减小、显示和增大按钮；支持固定粗细或与控制器压力相乘。
- 增加 NURBS、POLY 和 Bézier 控制点适配、可逆补丁注册与卸载恢复。
- 增加安全的开发目录联接安装脚本和 Freebird 源码契约验证脚本。

自动验证：

- Blender `3.6.23` 自带 Python `3.10.13` 已完成插件与测试代码语法编译。
- 扭转角、摇杆倍率、衰减函数、多 spline 遍历、连接衰减、切线计算和可逆补丁共 13 项单元测试已通过。
- Freebird 源码契约检查已通过，所需模块、类和函数均与 `2.14.2 / dd3cb84` 匹配。
- 已创建并核验开发目录联接：`C:\Users\LHT02\.freebird\plugins\freebird_curve_editor` → `D:\FreebirdPlugin\freebird_curve_editor`。

待验证：

- 当前有 Blender 实例正在运行，为保护未保存工作，没有启动竞争的后台 Blender，也没有执行 `Reload All`。
- 仍需在安全时机完成 Freebird 插件真实加载检查。
- 仍需使用 VR 控制器确认扭转方向、摇杆手感、衰减范围和同对象连续绘制的实际交互。
