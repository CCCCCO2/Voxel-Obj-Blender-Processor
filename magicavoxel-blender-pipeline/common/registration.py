import bpy

from ..common.properties import Properties

from ..voxel_cleanup.operator import VCP_MaterialUVSetter, VCP_VoxelCleanup
from ..voxel_cleanup.panel import VCP_Panel

from ..material_tools.operator import MT_RenameMaterialsByTexture, MT_FixDuplicateMaterials
from ..material_tools.panel import MT_Panel

from ..apply_mapping_scale_to_uv.operator import AMSTU_ApplyMappingScaleToUV
from ..apply_mapping_scale_to_uv.panel import AMSTU_Panel

from ..export_tools.operator import ET_ExportCollectionsToFBX
from ..export_tools.panel import ET_Panel

from ..object_group_tools.operator import (
    OGT_CreateGroup, OGT_AddToGroup, OGT_RemoveFromGroup,
    OGT_SelectGroup, OGT_HideGroups, OGT_ShowGroups, OGT_DissolveGroup,
)
from ..object_group_tools.panel import OGT_Panel



classes = (
    Properties,

    VCP_MaterialUVSetter,
    VCP_VoxelCleanup,
    VCP_Panel,

    AMSTU_ApplyMappingScaleToUV,
    AMSTU_Panel,

    MT_RenameMaterialsByTexture,
    MT_FixDuplicateMaterials,
    MT_Panel,
    
    ET_ExportCollectionsToFBX,
    ET_Panel,

    OGT_CreateGroup,
    OGT_AddToGroup,
    OGT_RemoveFromGroup,
    OGT_SelectGroup,
    OGT_HideGroups,
    OGT_ShowGroups,
    OGT_DissolveGroup,
    OGT_Panel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.vop_props = bpy.props.PointerProperty(type=Properties)


def unregister():
    if hasattr(bpy.types.Scene, "vop_props"):
        del bpy.types.Scene.vop_props

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
