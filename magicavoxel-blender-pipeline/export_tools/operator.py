import re
import bpy
import os

from bpy.types import Operator


class ET_ExportCollectionsToFBX(Operator):
    """按集合一键导出 FBX"""
    bl_idname = "mvbp.export_collections_fbx"
    bl_label = "按集合导出.FBX文件"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        props = context.scene.vop_props
        export_dir = bpy.path.abspath(props.export_directory)

        if not export_dir:
            self.report({'ERROR'}, "请选择导出目录")
            return {'CANCELLED'}

        os.makedirs(export_dir, exist_ok=True)
        old_selection = context.selected_objects[:]
        old_active = context.view_layer.objects.active

        export_count = 0

        try:

            for collection in bpy.data.collections:

                bpy.ops.object.select_all(action='DESELECT')

                mesh_objects = [
                    obj for obj in collection.objects
                    if obj.type == 'MESH'
                ]

                if not mesh_objects:
                    continue

                for obj in mesh_objects:
                    obj.select_set(True)

                context.view_layer.objects.active = mesh_objects[0]
                
                filename = re.sub(r'[<>:"/\\\\|?*]', "_", collection.name)

                filepath = os.path.join(
                    export_dir,
                    filename + ".fbx"
                )

                bpy.ops.export_scene.fbx(
                    filepath=filepath,
                    use_selection=True
                )

                export_count += 1

        finally:

            bpy.ops.object.select_all(action='DESELECT')

            for obj in old_selection:
                obj.select_set(True)

            context.view_layer.objects.active = old_active

        self.report(
            {'INFO'},
            f"共导出 {export_count} 个集合"
        )

        return {'导出完成'}