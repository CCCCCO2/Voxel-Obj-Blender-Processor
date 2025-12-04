import bpy

# 设置合并阈值
MERGE_DISTANCE = 0.0001

# 进入物体模式
if bpy.ops.object.mode_set.poll():
    bpy.ops.object.mode_set(mode='OBJECT')

for obj in bpy.context.selected_objects:
    if obj.type == 'MESH':
        # 设置为活动对象
        bpy.context.view_layer.objects.active = obj

        # 应用旋转和缩放
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        # 进入编辑模式
        if obj.mode != 'EDIT':
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
        bpy.ops.mesh.remove_doubles(threshold=MERGE_DISTANCE)

        # 删除松散顶点
        bpy.ops.mesh.delete_loose()
        
        # 更新网格
        obj.data.update()

        # 清除自定义拆分法向数据
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
            
        # 设置平直着色
        bpy.ops.mesh.faces_shade_flat()
        
        # 返回物体模式
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # 重新计算法向
        bpy.ops.object.shade_flat()
        
        # 清除所有材质槽
        obj.data.materials.clear()
        
        # 设置原点为几何中心
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        
# 清理未使用的数据
bpy.ops.outliner.orphans_purge()
print("批量处理完成！")