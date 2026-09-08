import bpy


class MT_Panel(bpy.types.Panel):
    """材质处理UI面板，包括重命名材质名以保证符合导入游戏引擎规范，处理模型的.001材质，以及合并Tiling应用到UV缩放后的重复材质等"""
    bl_label = "Material Tools"
    bl_idname = "MT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MV Blender Pipeline'

    def draw(self, context):
        layout = self.layout

        box_rmbt = layout.box()
        box_rmbt.label(text="重命名材质")
        box_rmbt.operator("mvbp.rename_by_texture", icon='MATERIAL')

        layout.separator()

        box_fdm = layout.box()
        box_fdm.label(text="修复材质")
        box_fdm.label(text="仅合并参数与贴图引用一致的材质")
        box_fdm.operator("mvbp.fix_duplicate_materials",icon='BRUSH_DATA')
