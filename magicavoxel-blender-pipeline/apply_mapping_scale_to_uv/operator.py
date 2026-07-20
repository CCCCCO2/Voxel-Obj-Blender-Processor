import bpy
import mathutils

from bpy.types import Operator


class AMSTU_ApplyMappingScaleToUV(Operator):
    """将 Mapping Scale 烘焙到 UV，并断开 Mapping"""
    bl_idname = "mvbp.apply_mapping_scale_to_uv"
    bl_label = "应用材质 Tilling 到 UV 缩放"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        material_users = {}

        # 收集所有材质对应的物体
        for obj in bpy.data.objects:

            if obj.type != 'MESH':
                continue

            for slot in obj.material_slots:

                mat = slot.material

                if mat is None:
                    continue

                material_users.setdefault(mat, []).append(obj)

        processed = 0

        for mat, objects in material_users.items():

            if not mat.use_nodes:
                continue

            nodes = mat.node_tree.nodes
            links = mat.node_tree.links

            for node in nodes:

                if node.type != 'TEX_IMAGE':
                    continue

                vector_input = node.inputs.get("Vector")

                if not vector_input or len(vector_input.links) == 0:
                    continue

                mapping = vector_input.links[0].from_node

                if mapping.type != 'MAPPING':
                    continue

                scale = mapping.inputs["Scale"].default_value.copy()

                for obj in objects:

                    mesh = obj.data

                    if len(mesh.uv_layers) == 0:
                        continue

                    uv_layer = mesh.uv_layers.active.data

                    center = mathutils.Vector((0.0, 0.0))
                    count = len(uv_layer)
                    for loop in uv_layer:
                        center += loop.uv

                    center /= count

                    for loop in uv_layer:
                        uv = loop.uv - center
                        uv.x *= scale.x
                        uv.y *= scale.y
                        loop.uv = center + uv

                    mesh.update()

                # 删除 Mapping → Image 的连接
                if len(mapping.inputs["Vector"].links) > 0:
                    links.remove(node.inputs["Vector"].links[0])

                self.report({'INFO'},f"处理中...处理完成材质{mat.name}对应所有使用物体的UV缩放")
                processed += 1

        self.report({'INFO'}, f"处理完毕，共处理 {processed} 个材质")

        return {'FINISHED'}