import bpy

from bpy.types import Operator
from mathutils import Matrix, Vector


def ancestors(obj):
    parent = obj.parent
    while parent:
        yield parent
        parent = parent.parent


def selected_roots(objects):
    selected = set(objects)
    return [obj for obj in objects if not any(p in selected for p in ancestors(obj))]


def subtree(roots):
    result = set()
    pending = list(roots)
    while pending:
        obj = pending.pop()
        if obj not in result:
            result.add(obj)
            pending.extend(obj.children)
    return result


def active_group(context):
    # Empty groups also support files made with the original version of this tool.
    return object_group(context.view_layer.objects.active)


def object_group(obj):
    while obj:
        if obj.type == 'EMPTY':
            return obj
        obj = obj.parent
    return None


def selected_group_objects(context):
    # 仅视口选择不会包括隐藏的大纲选择
    selected = {obj for obj in context.view_layer.objects
                if obj.select_get(view_layer=context.view_layer)}
    selected.update(obj for obj in getattr(context, 'selected_ids', ())
                    if isinstance(obj, bpy.types.Object)
                    and obj.name in context.view_layer.objects)
    # 隐藏的轮廓行可能会被选中 即使视口选择未同步
    if context.screen:
        for area in context.screen.areas:
            if area.type == 'OUTLINER':
                region = next((r for r in area.regions if r.type == 'WINDOW'), None)
                if region is None:
                    continue
                # 侧边栏的用户界面区域无法提供大纲选中的 ID
                with context.temp_override(area=area, region=region):
                    selected.update(obj for obj in getattr(context, 'selected_ids', ())
                                    if isinstance(obj, bpy.types.Object)
                                    and obj.name in context.view_layer.objects)
    return selected


def target_collection(context, active):
    collections = active.users_collection
    return context.collection if context.collection in collections else collections[0]


def move_to_collection(objects, collection):
    for obj in objects:
        if collection not in obj.users_collection:
            collection.objects.link(obj)
        for old in list(obj.users_collection):
            if old != collection:
                old.objects.unlink(obj)


def reparent(objects, parent):
    matrices = {obj: obj.matrix_world.copy() for obj in objects}
    for obj in objects:
        basis = obj.matrix_basis.copy()
        obj.parent = parent
        obj.parent_type = 'OBJECT'
        if parent:
            # 保留父逆矩阵中的继承剪切
            if abs(basis.determinant()) < 1e-12:
                basis = Matrix.Identity(4)
            obj.matrix_parent_inverse = parent.matrix_world.inverted() @ matrices[obj] @ basis.inverted()
            obj.matrix_basis = basis
        else:
            obj.matrix_parent_inverse = Matrix.Identity(4)
            obj.matrix_world = matrices[obj]


def can_detach(operator, objects, parent):
    if parent:
        return True
    for obj in objects:
        world = obj.matrix_world
        rebuilt = Matrix.LocRotScale(*world.decompose())
        if any(abs(world[i][j] - rebuilt[i][j]) > 1e-5 for i in range(3) for j in range(3)):
            operator.report({'WARNING'}, "成员包含父级产生的剪切变换，无法无损移到场景根级；请先整理父级旋转和非均匀缩放")
            return False
    return True


def select_objects(context, objects, active):
    for obj in list(context.selected_objects):
        obj.select_set(False)
    for obj in objects:
        if obj.name in context.view_layer.objects:
            obj.select_set(True)
    context.view_layer.objects.active = active


def validate(operator, objects, collection=None, parent=None):
    if any(not obj.is_editable for obj in objects) or (collection and not collection.is_editable):
        operator.report({'WARNING'}, "对象或集合不可编辑，请先转为本地数据")
        return False
    if parent and abs(parent.matrix_world.determinant()) < 1e-12:
        operator.report({'WARNING'}, "父级缩放不可逆，请先修正零缩放")
        return False
    return True


class GroupOperator:
    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.view_layer.objects.active is not None


class OGT_CreateGroup(GroupOperator, Operator):
    """将选中物体创建为新组，保留内部层级，并将所有成员及后代移动到活动物体所在集合"""
    bl_idname = "mvbp.object_group"
    bl_label = "创建新组"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = list(context.selected_objects)
        active = context.view_layer.objects.active
        if not selected or active not in selected:
            self.report({'WARNING'}, "请选择物体并指定活动物体")
            return {'CANCELLED'}
        roots = selected_roots(selected)
        members = subtree(roots)
        collection = target_collection(context, active)
        if not validate(self, members, collection):
            return {'CANCELLED'}
        center = sum((obj.matrix_world.translation for obj in selected), Vector()) / len(selected)
        name = context.scene.vop_props.parent_object_name.strip() or "Root"
        empty = bpy.data.objects.new(name, None)
        empty.empty_display_type = 'PLAIN_AXES'
        collection.objects.link(empty)
        empty.location = center
        context.view_layer.update()
        reparent(roots, empty)
        move_to_collection(members, collection)
        select_objects(context, [empty], empty)
        self.report({'INFO'}, f"已创建组 '{empty.name}'，{len(members)} 个成员已移动到集合 '{collection.name}'")
        return {'FINISHED'}


class OGT_AddToGroup(GroupOperator, Operator):
    """最后选中目标组根节点或组内成员，将其他选中物体及后代加入该组"""
    bl_idname = "mvbp.object_group_add"
    bl_label = "加入已有组"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        group = active_group(context)
        if not group:
            self.report({'WARNING'}, "请将目标组根节点或组内成员设为活动物体")
            return {'CANCELLED'}
        candidates = [obj for obj in context.selected_objects if obj != group]
        if any(obj in ancestors(group) for obj in candidates):
            self.report({'WARNING'}, "不能将目标组的祖先加入该组")
            return {'CANCELLED'}
        roots = selected_roots([obj for obj in candidates if group not in ancestors(obj)])
        if not roots:
            self.report({'WARNING'}, "请选择需要加入的组外物体")
            return {'CANCELLED'}
        collection = target_collection(context, context.view_layer.objects.active)
        members = subtree([group]) | subtree(roots)
        if not validate(self, members, collection, group):
            return {'CANCELLED'}
        reparent(roots, group)
        move_to_collection(members, collection)
        select_objects(context, [group], group)
        self.report({'INFO'}, f"已加入组 '{group.name}'，成员统一移动到集合 '{collection.name}'")
        return {'FINISHED'}


class OGT_RemoveFromGroup(GroupOperator, Operator):
    """将选中成员及其子树移到所属组的父级，保持集合和世界变换"""
    bl_idname = "mvbp.object_group_remove"
    bl_label = "移出组"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        roots = selected_roots(list(context.selected_objects))
        moves = []
        for obj in roots:
            group = next((p for p in ancestors(obj) if p.type == 'EMPTY'), None)
            if group:
                moves.append((obj, group.parent))
        if not moves:
            self.report({'WARNING'}, "请选择组内需要移出的成员")
            return {'CANCELLED'}
        for obj, parent in moves:
            if not validate(self, [obj], parent=parent) or not can_detach(self, [obj], parent):
                return {'CANCELLED'}
        for obj, parent in moves:
            reparent([obj], parent)
        self.report({'INFO'}, f"已移出 {len(moves)} 个成员子树，集合归属保持不变")
        return {'FINISHED'}


class OGT_SelectGroup(GroupOperator, Operator):
    """选中当前组的根节点及全部成员；嵌套分组时定位最近一层组"""
    bl_idname = "mvbp.object_group_select"
    bl_label = "选择整组物体"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        group = active_group(context)
        if not group:
            self.report({'WARNING'}, "请选择组根节点或组内成员")
            return {'CANCELLED'}
        members = subtree([group])
        select_objects(context, members, group)
        selected = set(context.selected_objects)
        skipped = len(members - selected)
        self.report({'WARNING'} if skipped else {'INFO'},
                    f"已选择 {len(members & selected)} 个对象" +
                    (f"，{skipped} 个隐藏或不可选对象未选中" if skipped else ""))
        return {'FINISHED'}


class GroupVisibilityOperator:
    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and bool(selected_group_objects(context))

    def execute(self, context):
        groups = {object_group(obj) for obj in selected_group_objects(context)}
        groups.discard(None)
        if not groups:
            self.report({'WARNING'}, "请选择组根节点或组内成员")
            return {'CANCELLED'}
        members = subtree(groups)
        layer = context.view_layer
        available = [obj for obj in members if obj.name in layer.objects]
        for obj in available:
            if not self.hide_group:
                obj.hide_viewport = False
            obj.hide_set(self.hide_group, view_layer=layer)
        skipped = len(members) - len(available)
        action = "隐藏" if self.hide_group else "恢复视图显示"
        message = f"已为 {len(groups)} 个组的 {len(available)} 个物体{action}"
        if skipped:
            message += f"，{skipped} 个物体不在当前视图层中，已跳过"
        if not self.hide_group:
            blocked = sum(not obj.visible_get(view_layer=layer) for obj in available)
            if blocked:
                message += f"，{blocked} 个物体仍受集合或其他可见性设置限制"
        self.report({'WARNING'} if skipped else {'INFO'}, message)
        return {'FINISHED'}


class OGT_HideGroups(GroupVisibilityOperator, Operator):
    """隐藏所有选中物体所属组的根节点及全部后代；支持多组，无需活动物体，仅影响当前视图层"""
    bl_idname = "mvbp.object_group_hide"
    bl_label = "隐藏整组物体"
    bl_options = {'REGISTER', 'UNDO'}
    hide_group = True


class OGT_ShowGroups(GroupVisibilityOperator, Operator):
    """包含大纲视图中选中的隐藏物体，恢复其所属组下全部物体的视图显示，无需活动物体"""
    bl_idname = "mvbp.object_group_show"
    bl_label = "显示整组物体"
    bl_options = {'REGISTER', 'UNDO'}
    hide_group = False


class OGT_DissolveGroup(GroupOperator, Operator):
    """删除当前组的根节点，将直接子物体提升到原父级，保留成员、内部层级和集合"""
    bl_idname = "mvbp.object_group_dissolve"
    bl_label = "解散组"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        group = active_group(context)
        if not group:
            self.report({'WARNING'}, "请选择要解散的组根节点或组内成员")
            return {'CANCELLED'}
        return context.window_manager.invoke_confirm(
            self, event,
            title=f"确认解散组 '{group.name}'？",
            message="将删除组根节点，保留组内物体、内部层级和集合归属。",
            confirm_text="确认解散",
            icon='WARNING',
        )

    def execute(self, context):
        group = active_group(context)
        if not group:
            self.report({'WARNING'}, "请选择要解散的组根节点或组内成员")
            return {'CANCELLED'}
        children = list(group.children)
        if not validate(self, [group] + children, parent=group.parent):
            return {'CANCELLED'}
        if not can_detach(self, children, group.parent):
            return {'CANCELLED'}
        reparent(children, group.parent)
        bpy.data.objects.remove(group, do_unlink=True)
        visible = [obj for obj in children if obj.name in context.view_layer.objects]
        select_objects(context, visible, visible[0] if visible else None)
        self.report({'INFO'}, "已解散组，成员及内部层级已保留")
        return {'FINISHED'}
