import bpy
import re
import os


class MT_RenameMaterialsByTexture(bpy.types.Operator):
    """根据贴图重命名材质"""
    bl_idname = "mvbp.rename_by_texture"
    bl_label = "根据贴图快速重命名所有材质球"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        renamed_count = 0

        for material in bpy.data.materials:

            if not material.use_nodes:
                continue

            image_name = None

            # 查找 Image Texture 节点
            for node in material.node_tree.nodes:

                if node.type != 'TEX_IMAGE':
                    continue

                if node.image is None:
                    continue

                # name = node.image.name
                # name = os.path.splitext(node.image.name)[0]
                # match = re.match(r"^T_(.+?)_(C|D|BaseColor|Normal|ARM|Emission|Mask|Height|AO)(\..+)?$", name)
                
                name = os.path.splitext(node.image.name)[0]

                # 去掉 Blender 自动添加的 .001 等后缀
                name = re.sub(r"\.\d+$", "", name)
                # 去掉 T_
                if name.startswith("T_"):
                    name = name[2:]
                # 去掉贴图类型后缀
                for suffix in (
                    "_BaseColor",
                    "_Normal",
                    "_ARM",
                    "_Emission",
                    "_Mask",
                    "_Height",
                    "_AO",
                    "_C",
                    "_D",
                ):
                    if name.endswith(suffix):
                        name = name[:-len(suffix)]
                        break

                if name:
                    name = name[0].upper() + name[1:]

                image_name = name
                break
    
                if match:
                    image_name = match.group(1)
                    break

            if image_name is None:
                continue

            new_name = f"M_{image_name}"

            if material.name != new_name:
                material.name = new_name
                renamed_count += 1

        self.report({'INFO'}, f"成功重命名 {renamed_count} 个材质")

        return {'FINISHED'}


class MT_FixDuplicateMaterials(bpy.types.Operator):
    """修复.001等重复材质"""
    bl_idname = "mvbp.fix_duplicate_materials"
    bl_label = "修复重复材质(.001)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        replace_count = 0
        rename_count = 0
        remove_count = 0

        # 复制列表，防止删除时遍历失效
        materials = list(bpy.data.materials)

        for mat in materials:

            match = re.match(r"^(.*)\.(\d+)$", mat.name)

            if match is None:
                continue

            original_name = match.group(1)

            # -------------------------
            # 有原材质
            # -------------------------
            if original_name in bpy.data.materials:

                original = bpy.data.materials[original_name]

                if original == mat:
                    continue

                # 修改所有物体引用
                for obj in bpy.data.objects:

                    for slot in obj.material_slots:

                        if slot.material == mat:
                            slot.material = original
                            replace_count += 1

                bpy.data.materials.remove(mat)

                remove_count += 1

            # -------------------------
            # 没有原材质
            # -------------------------
            else:

                mat.name = original_name
                rename_count += 1

        self.report(
            {'INFO'},
            f"替换 {replace_count} 个引用，删除 {remove_count} 个重复材质，重命名 {rename_count} 个材质"
        )

        return {'FINISHED'}
