import bpy


class COGT_Panel(bpy.types.Panel):
    """相机遮挡组工具 UI 面板"""
    bl_label = "CameraOcclusionGroupTools"
    bl_idname = "COGT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MV Blender Pipeline"

    def draw(self, context):
        layout = self.layout
        props = context.scene.vop_props

        col = layout.column()
        col.prop(props, "parent_object_name")
        col.separator()
        col.operator("mvbp.camera_occlusion_group", icon='EMPTY_AXIS')
