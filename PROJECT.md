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
