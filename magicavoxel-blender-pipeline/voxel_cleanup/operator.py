import bpy

class VCP_VoxelCleanup(bpy.types.Operator):
    """清理选中物体的网格（融并、合并顶点、平滑法向等）"""
    bl_idname = "mvbp.voxel_cleanup"
    bl_label = "执行网格清理"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.vop_props
        merge_distance = props.merge_distance

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')

        selected_objs = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_objs:
            self.report({'WARNING'}, "未选择任何网格物体")
            return {'CANCELLED'}

        for obj in selected_objs:
            # 设置为活动对象
            context.view_layer.objects.active = obj

            # 应用旋转和缩放
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

            # 进入编辑模式
            bpy.ops.object.mode_set(mode='EDIT')
                
            # 切换到面选择模式，并选择所有面
            bpy.ops.mesh.select_mode(type='FACE')
            bpy.ops.mesh.select_all(action='SELECT')
                
            # 有限融并
            bpy.ops.mesh.dissolve_limited()

            # 切换到点选择模式，并选择所有点
            bpy.ops.mesh.select_mode(type='VERT')
            bpy.ops.mesh.select_all(action='SELECT')

            # 合并顶点
            bpy.ops.mesh.remove_doubles(threshold=merge_distance)

            # 删除松散顶点
            bpy.ops.mesh.delete_loose()
            
            # 更新网格 (在编辑模式下退出会自动更新，显式调用也可以)
            obj.data.update()

            # 清除自定义拆分法向数据
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
                
            # 设置平直着色 (需在编辑模式特定操作或物体模式)
            bpy.ops.mesh.faces_shade_flat()
            
            # 返回物体模式
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # 重新计算法向 (物体级别)
            bpy.ops.object.shade_flat()
            
            # 清除所有材质槽
            obj.data.materials.clear()
            
            # 设置原点为几何中心
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        
        # 清理未使用的数据
        bpy.ops.outliner.orphans_purge()
        
        self.report({'INFO'}, f"批量清理完成！")
        return {'FINISHED'}


class VCP_MaterialUVSetter(bpy.types.Operator):
    """为指定集合内的物体进行立方体投影UV展开并设置材质"""
    bl_idname = "mvbp.material_uv_setter"
    bl_label = "展开UV并应用材质"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.vop_props
        collection_obj = props.target_collection
        material_obj = props.target_material
        cube_size = props.cube_size
        
        if not collection_obj:
            self.report({'ERROR'}, "请先选择目标集合")
            return {'CANCELLED'}
            
        collection_name = collection_obj.name
        
        # 材质处理
        mat = material_obj
        use_exist_mat = True
        if not mat:
            material_name = f"Mat_{collection_name}"
            mat = bpy.data.materials.new(name=material_name)
            mat.use_nodes = True
            use_exist_mat = False
        else:
            material_name = mat.name
            
        collection = collection_obj
        
        if collection:
            for obj in collection.objects:
                if obj.type == 'MESH':
                    obj.data.materials.clear()
                    obj.data.materials.append(mat)
                    
                    bpy.context.view_layer.objects.active = obj
                    
                    if obj.mode != 'EDIT':
                        bpy.ops.object.mode_set(mode='EDIT')
                    
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.uv.cube_project(cube_size=cube_size)
                    bpy.ops.object.mode_set(mode='OBJECT')
            
            msg = f"已为集合'{collection_name}'中物体应用尺寸为'{cube_size}'的立方体投影UV展开"
            if use_exist_mat:
                msg += f"，并应用已有材质'{material_name}'"
            else:
                msg += f"，并创建新材质'{material_name}'"
            
            self.report({'INFO'}, msg)
            return {'FINISHED'}
            
        else:
            self.report({'ERROR'}, f"未找到集合 '{collection_name}'")
            return {'CANCELLED'}
