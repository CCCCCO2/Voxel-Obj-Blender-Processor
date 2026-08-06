import bpy

from bpy.types import Operator
from mathutils import Matrix, Vector


class COGT_ParentSelectedToEmpty(Operator):
    """在所选物体的平均轴心处创建空物体，并保持世界变换建立父子关系"""
    bl_idname = "mvbp.camera_occlusion_group"
    bl_label = "创建空物体父级"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.mode != 'OBJECT':
            self.report({'WARNING'}, "请先切换到物体模式")
            return {'CANCELLED'}

        selected_objects = list(context.selected_objects)
        if not selected_objects:
            self.report({'WARNING'}, "请至少选择一个物体")
            return {'CANCELLED'}

        active_object = context.view_layer.objects.active
        center = sum(
            (obj.matrix_world.translation for obj in selected_objects),
            Vector()
        ) / len(selected_objects)
        world_matrices = {
            obj: obj.matrix_world.copy()
            for obj in selected_objects
        }

        requested_name = context.scene.vop_props.parent_object_name.strip()
        empty = bpy.data.objects.new(requested_name or "Root", None)
        empty.empty_display_type = 'PLAIN_AXES'
        empty.location = center

        target_collection = context.collection
        if active_object and active_object.users_collection:
            if target_collection not in active_object.users_collection:
                target_collection = active_object.users_collection[0]
        target_collection.objects.link(empty)

        # Root 只有位移、没有旋转和缩放，因此子物体的新局部坐标就是：
        # 子物体原世界坐标 - Root 世界坐标。
        for obj in selected_objects:
            local_matrix = world_matrices[obj].copy()
            local_matrix.translation = (
                world_matrices[obj].translation - center
            )

            obj.parent = empty
            obj.matrix_parent_inverse = Matrix.Identity(4)
            obj.matrix_basis = local_matrix

        bpy.ops.object.select_all(action='DESELECT')
        empty.select_set(True)
        context.view_layer.objects.active = empty

        self.report(
            {'INFO'},
            f"已将 {len(selected_objects)} 个物体放到空物体 '{empty.name}' 下"
        )
        return {'FINISHED'}
