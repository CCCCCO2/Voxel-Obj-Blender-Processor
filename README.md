# MagicaVoxel-Blender-Pipeline

这是一个 专为 MagicaVoxel -> Blender -> 游戏引擎 工作流程设计的 Blender Extension。它集成了一系列针对 MagicaVoxel 导出模型的处理工具，可自动完成网格清理、UV 处理、材质整理、贴图处理以及资源导出等操作，帮助模型快速进入 Unity 等游戏开发流程。

目前插件包含以下功能模块：

- Voxel Cleanup
	- 清理 MagicaVoxel 导出的 OBJ 模型
	- 有限融并（Limited Dissolve）
	- 合并重合顶点
	- 删除松散几何
	- 清除法线数据
	- 平面着色
	- 自动设置原点
- UV Tools
	- 对指定集合执行 Cube Projection
	- 自动应用材质
	- 将 Mapping 节点的 UV Scale 烘焙到模型 UV
- Material Tools
	- 根据贴图自动重命名材质
	- 修复重复材质
Export Tools
	- 按 Collection 批量导出 FBX
	- 支持自定义输出目录

## 安装方法

**版本兼容性警告**：本项目主要维护 Blender 4.2+ Extension，旧的脚本仅包含 Voxel Cleanup 功能。如要使用完全功能请使用 Blender 4.2 及以上版本

#### Blender 4.2 及以上版本

 请使用 Blender Extensions 的 .zip 扩展插件</br>

1. 下载 .zip 扩展插件
2. 在 Blender 中选择“编辑”  -> “偏好设置...” -> “插件” -> “从磁盘安装...”，找到下载的插件安装


#### Blender 4.2以下版本

请使用传统 .py 脚本文件

**不完全功能警告**：传统脚本仅包含 Voxel Cleanup 功能，暂时没有更新维护的计划

1. 下载脚本
2. 在 Blender 中打开“文本编辑器”视图：
  - 选择“打开”
  - 找到并选择下载的脚本文件载入
  - 点击“运行脚本”

## 用户手册

请根据您的 Blender 版本选择相应的手册

#### Blender 4.2 及以上版本

如果您使用的是最新的 Blender 版本，请参考 Extensions 插件手册

* [Blender Extensions 版本手册](docs/Extensions/新版本插件手册.md)

#### Blender 4.2以下版本

如果您使用的是旧版本的 Blender，请参考这份兼容性手册进行安装和使用

* [旧版本兼容手册（适用于 Blender < 4.2）](docs/CompatibleVersion/旧版本兼容手册.md)