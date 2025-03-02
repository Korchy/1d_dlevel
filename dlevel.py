# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/1d_dlevel

from bpy.types import Operator, Panel
from bpy.utils import register_class, unregister_class
from mathutils import Vector
from mathutils.bvhtree import BVHTree

bl_info = {
    "name": "DLevel",
    "description": "Drops all selected objects by global Z-axis until their origins will not stay on the surface object (active object).",
    "author": "Nikita Akimov, Paul Kotelevets",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Tool panel > 1D > DLevel",
    "doc_url": "https://github.com/Korchy/1d_dlevel",
    "tracker_url": "https://github.com/Korchy/1d_dlevel",
    "category": "All"
}


# MAIN CLASS

class DLevel:

    @classmethod
    def dlevel(cls, selected_objects, dest_object):
        # moves all selected objects by global Z-axis until their origins will not intersect active object
        if selected_objects and dest_object:
            # get all selected objects origins coordinates
            src_objects = [(obj, obj.location) for obj in selected_objects if obj != dest_object]
            # create BVH tree for dest object faces
            dest_world_matrix = dest_object.matrix_world.copy()
            dest_vertices_world = [dest_world_matrix * vertex.co for vertex in dest_object.data.vertices]
            dest_faces = [polygon.vertices for polygon in dest_object.data.polygons]
            dest_bvh_tree = BVHTree.FromPolygons(dest_vertices_world, dest_faces, all_triangles=False, epsilon=0.0)
            # for each src_object's location cast rays down (0.0, 0.0, -1.0) and up (0.0, 0.0, 1.0) directions
            #   and check hit with dest_bvh_tree faces
            raycasts = [(obj[0], dest_bvh_tree.ray_cast(obj[1], Vector((0.0, 0.0, -1.0))), dest_bvh_tree.ray_cast(obj[1], Vector((0.0, 0.0, 1.0))))
                        for obj in src_objects]
            # for each raycast result get distance to crossing point
            for obj, raycast_down, raycast_up in raycasts:
                if raycast_up != (None, None, None, None) or raycast_down != (None, None, None, None) :
                    # has at leash one intersect with up or down
                    distance_up = raycast_up[3]
                    distance_down = raycast_down[3]
                    if distance_up is not None and distance_down is not None:
                        # has intersection up and down - move to upper
                        lu = obj.location.z + (distance_up if distance_up else 0.0)
                        ld = obj.location.z - (distance_down if distance_down else 0.0)
                        obj.location.z = max(lu, ld)
                    elif distance_up is not None:
                        # has intersection only by up ray
                        obj.location += Vector((0.0, 0.0, distance_up))
                    elif distance_down is not None:
                        # has intersection only by down ray
                        obj.location += Vector((0.0, 0.0, -distance_down))

    @staticmethod
    def ui(layout, context):
        # ui panel
        layout.operator(
            operator='dlevel.dlevel',
            icon='FORCE_DRAG'
        )

# OPERATORS

class DLevel_OT_dlevel(Operator):
    bl_idname = 'dlevel.dlevel'
    bl_label = 'DLevel'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        DLevel.dlevel(
            selected_objects=context.selected_objects,
            dest_object=context.active_object
        )
        return {'FINISHED'}


# PANELS

class DLevel_PT_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'DLevel'
    bl_category = '1D'

    def draw(self, context):
        DLevel.ui(
            layout=self.layout,
            context=context
        )


# REGISTER

def register(ui=True):
    register_class(DLevel_OT_dlevel)
    if ui:
        register_class(DLevel_PT_panel)


def unregister(ui=True):
    if ui:
        unregister_class(DLevel_PT_panel)
    unregister_class(DLevel_OT_dlevel)


if __name__ == '__main__':
    register()
