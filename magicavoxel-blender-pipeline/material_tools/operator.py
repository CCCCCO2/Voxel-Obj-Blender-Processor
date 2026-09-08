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


# Only editor presentation is ignored. Unknown/animated data is kept intact.
_NODE_UI = {'name', 'label', 'location', 'location_absolute', 'width', 'height', 'dimensions',
            'select', 'show_options', 'show_preview', 'hide', 'use_custom_color',
            'color', 'parent', 'inputs', 'outputs', 'internal_links'}
_ID_METADATA = set(bpy.types.ID.bl_rna.properties.keys())


def _rna_settings(value, ignored=(), depth=0):
    if depth > 12:
        raise ValueError('Unsupported recursive settings')
    try:
        if any(key not in value.bl_rna.properties for key in value.keys()):
            raise ValueError('Custom properties require manual review')
    except TypeError:
        pass  # Some built-in RNA structures cannot store custom properties.
    result = []
    for prop in value.bl_rna.properties:
        key = prop.identifier
        if key in {'rna_type', 'id_data'} or key in ignored:
            continue
        if prop.is_readonly and prop.type not in {'POINTER', 'COLLECTION'}:
            continue
        item = getattr(value, key)
        if prop.type == 'POINTER':
            if item is None:
                data = None
            elif isinstance(item, bpy.types.ID):
                data = ('ID', item.as_pointer())
            else:
                data = _rna_settings(item, depth=depth + 1)
        elif prop.type == 'COLLECTION':
            data = tuple(_rna_settings(child, depth=depth + 1) for child in item)
        elif getattr(prop, 'is_array', False):
            data = tuple(item)
        elif isinstance(item, set):
            data = tuple(sorted(item))
        else:
            data = item
        result.append((key, data))
    return (value.bl_rna.identifier, tuple(result))


def _material_signature(material):
    if (material.library or material.override_library or material.asset_data
            or material.animation_data or material.use_fake_user
            or not material.is_editable):
        raise ValueError('Protected or animated material')
    settings = _rna_settings(material, _ID_METADATA | {'node_tree', 'animation_data'})
    tree = material.node_tree
    if tree is None:
        return settings, None
    if tree.animation_data:
        raise ValueError('Animated node tree')
    tree_settings = _rna_settings(
        tree, _ID_METADATA | {'nodes', 'links', 'interface', 'animation_data'})
    nodes = []
    # Match copied nodes by name. Renamed/rebuilt graphs are conservatively kept.
    for node in sorted(tree.nodes, key=lambda item: item.name):
        sockets = []
        for socket in (*node.inputs, *node.outputs):
            sockets.append((socket.identifier, _rna_settings(
                socket, {'node', 'links', 'name', 'description', 'hide',
                         'hide_value', 'show_expanded', 'display_shape'})))
        nodes.append((node.name, node.bl_idname,
                      _rna_settings(node, _NODE_UI), tuple(sockets)))
    links = tuple(sorted((link.from_node.name, link.from_socket.identifier,
                          link.to_node.name, link.to_socket.identifier,
                          link.is_muted, link.multi_input_sort_id)
                         for link in tree.links))
    return settings, tree_settings, tuple(nodes), links


def materials_equivalent(first, second):
    """Only merge materials whose supported settings and references match exactly."""
    try:
        return _material_signature(first) == _material_signature(second)
    except (AttributeError, TypeError, ValueError, RuntimeError, RecursionError):
        return False


class MT_FixDuplicateMaterials(bpy.types.Operator):
    """仅合并参数、节点连接及贴图引用一致的同名后缀材质，保留有差异的材质"""
    bl_idname = "mvbp.fix_duplicate_materials"
    bl_label = "修复重复材质(.001)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        remove_count = rename_count = kept_count = 0
        for mat in list(bpy.data.materials):
            match = re.match(r"^(.*)\.(\d+)$", mat.name)
            if match is None:
                continue
            original_name = match.group(1)
            original = bpy.data.materials.get(original_name)
            if original is not None:
                if not materials_equivalent(mat, original):
                    kept_count += 1
                    continue
                # Remap every datablock reference, including meshes without objects.
                mat.user_remap(original)
                bpy.data.materials.remove(mat)
                remove_count += 1
            elif mat.is_editable and not mat.library and not mat.override_library:
                mat.name = original_name
                rename_count += 1
            else:
                kept_count += 1
        self.report({'INFO'},
                    f"合并 {remove_count} 个相同材质，保留 {kept_count} 个存在差异或无法确认的材质，"
                    f"重命名 {rename_count} 个无同名原材质的材质")
        return {'FINISHED'}
