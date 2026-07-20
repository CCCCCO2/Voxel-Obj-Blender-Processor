import bpy


class AMSTU_Panel(bpy.types.Panel):
    """一键应用材质Tilling到UV缩放UI面板"""
    bl_label = "UV Tools"
    bl_idname = "AMSTU_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MV Blender Pipeline"

    def draw(self, context):

        layout = self.layout
        layout.operator("mvbp.apply_mapping_scale_to_uv", icon='UV')
