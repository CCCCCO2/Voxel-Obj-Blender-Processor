import bpy


class ET_Panel(bpy.types.Panel):
    """导出工具UI面板"""
    bl_label = "Export Tools"
    bl_idname = "ET_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MV Blender Pipeline"

    def draw(self, context):

        layout = self.layout

        props = context.scene.vop_props

        col = layout.column()
        col.prop(props, "export_directory")

        col.separator()

        col.operator("mvbp.export_collections_fbx", icon='EXPORT')