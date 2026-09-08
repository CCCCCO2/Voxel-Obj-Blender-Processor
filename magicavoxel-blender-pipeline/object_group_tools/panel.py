import bpy


class OGT_Panel(bpy.types.Panel):
    """物体分组工具 UI 面板"""
    bl_label = "Object Group Tools"
    bl_idname = "OGT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MV Blender Pipeline"

    def draw(self, context):
        layout = self.layout
        props = context.scene.vop_props

        col = layout.column()
        col.prop(props, "parent_object_name")
        col.separator()
        col.operator("mvbp.object_group", icon='EMPTY_AXIS')
        col.separator()
        col.label(text="目标：选中的组根节点或成员所属组")
        col.label(text="嵌套分组时，定位最近一层组")
        col.operator("mvbp.object_group_add", icon='ADD')
        col.operator("mvbp.object_group_remove", icon='REMOVE')
        col.operator("mvbp.object_group_select", icon='RESTRICT_SELECT_OFF')
        col.operator("mvbp.object_group_hide", icon='HIDE_ON')
        col.operator("mvbp.object_group_show", icon='HIDE_OFF')
        row = col.row()
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator("mvbp.object_group_dissolve", icon='UNLINKED')
