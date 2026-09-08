import bpy
from bpy.props import StringProperty

class Properties(bpy.types.PropertyGroup):
    # UV Setter 的属性
    target_collection: bpy.props.PointerProperty(
        name="目标集合",
        description="需要处理的目标集合",
        type=bpy.types.Collection
    )
    target_material: bpy.props.PointerProperty(
        name="目标材质",
        description="应用的材质名称 (不存在则新建)",
        type=bpy.types.Material
    )
    cube_size: bpy.props.FloatProperty(
        name="立方体投影尺寸",
        description="立方体投影的大小",
        default=5.12,
        min=0.01
    )
    
    # Voxel Cleanup 的属性
    merge_distance: bpy.props.FloatProperty(
        name="合并阈值",
        description="合并顶点的距离阈值",
        default=0.0001,
        precision=5,
        step=0.0001,
        min=0.0
    )

    # 导出工具的属性
    export_directory: StringProperty(
        name="导出目录",
        description="FBX 导出的目标目录",
        subtype='DIR_PATH'
    )

    # Object Group Tools 的属性
    parent_object_name: StringProperty(
        name="组名称",
        description="新建组的名称，用于命名组根节点；留空时使用 Root",
        default="Root"
    )
