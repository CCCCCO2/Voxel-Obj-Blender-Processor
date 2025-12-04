import bpy

# 设置集合名称，该集合下的所有 mesh 将会设置一个统一的材质
collection_name = ""
# 设置材质名称，若该材质名存在于缓存数据中，则设置为该材质，否则会新建一个该名称的空材质
material_name = ""

# 默认立方体投影的立方体尺寸
CUBE_SIZE = 5.12

if material_name in bpy.data.materials:
    mat = bpy.data.materials[material_name]
    use_exist_mat = True
else:
    mat = bpy.data.materials.new(name = material_name)
    use_exist_mat = False
    mat.use_nodes = True
    
collection = bpy.data.collections.get(collection_name)
if collection:
    for obj in collection.objects:
        if obj.type == 'MESH':
            obj.data.materials.clear()
            obj.data.materials.append(mat)
            
            bpy.context.view_layer.objects.active = obj
            if obj.mode != 'EDIT':
                bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.cube_project(cube_size=CUBE_SIZE)
            bpy.ops.object.mode_set(mode='OBJECT')
            
    if use_exist_mat:
        print(f"已为集合'{collection_name}'中物体应用尺寸为'{CUBE_SIZE}'的立方体投影UV展开，并应用已有材质'{material_name}'")
    else:
        print(f"已为集合'{collection_name}'中物体应用尺寸为'{CUBE_SIZE}'的立方体投影UV展开，并创建新材质'{material_name}'")
else:
    print(f"未找到集合'{collection_name}'，请检查集合名称是否正确")