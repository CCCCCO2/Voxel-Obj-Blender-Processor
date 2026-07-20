import bpy

class VCP_Panel(bpy.types.Panel):
    """导入voxel模型预处理UI面板"""
    bl_label = "Voxel Clean Up"
    bl_idname = "VCP_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MV Blender Pipeline'

    def draw(self, context):
        layout = self.layout
        props = context.scene.vop_props
        scene = context.scene

        # VoxelCleanup
        box_vc = layout.box()
        box_vc.label(text="Voxel清理工具", icon='MESH_DATA')
        
        # 变量设置
        col_vc = box_vc.column()
        col_vc.prop(props, "merge_distance")
        # 按钮
        col_vc.separator()
        col_vc.operator("mvbp.voxel_cleanup", icon='BRUSH_DATA')

        layout.separator()

        # VCP_MaterialUVSetter
        box_ms = layout.box()
        box_ms.label(text="展开UV并应用材质", icon='MATERIAL')
        
        # 变量设置
        col_ms = box_ms.column()
        col_ms.prop(props, "target_collection")
        col_ms.prop(props, "target_material")
        col_ms.prop(props, "cube_size")
        # 按钮
        col_ms.separator()
        col_ms.operator("mvbp.material_uv_setter", icon='UV')
