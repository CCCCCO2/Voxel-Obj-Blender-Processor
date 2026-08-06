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

            # 只处理当前视图层中、场景根集合直属的可见集合。
            # 子集合的对象会合并到父集合的 FBX 中，不再单独生成文件。
            top_level_collections = [
                layer_collection.collection
                for layer_collection in context.view_layer.layer_collection.children
                if layer_collection.visible_get()
            ]

            for collection in top_level_collections:

                bpy.ops.object.select_all(action='DESELECT')

                mesh_objects = [
                    obj for obj in collection.all_objects
                    if obj.type == 'MESH'
                    and obj.visible_get(view_layer=context.view_layer)
                ]

                if not mesh_objects:
                    continue

                export_objects = [
                    obj for obj in collection.all_objects
                    if obj.type in {'MESH', 'EMPTY'}
                    and obj.visible_get(view_layer=context.view_layer)
                ]

                for obj in export_objects:
                    obj.select_set(True)

                context.view_layer.objects.active = mesh_objects[0]
                
                filename = re.sub(r'[<>:"/\\\\|?*]', "_", collection.name)

                filepath = os.path.join(
                    export_dir,
                    filename + ".fbx"
                )

                bpy.ops.export_scene.fbx(
                    filepath=filepath,
                    use_selection=True,
                    object_types={'MESH', 'EMPTY'}
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

        return {'FINISHED'}
