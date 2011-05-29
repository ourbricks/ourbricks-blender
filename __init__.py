'''
OurBricks-Blender

Copyright (c) 2011, Katalabs Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:
 * Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in
   the documentation and/or other materials provided with the
   distribution.
 * Neither the name of Sirikata nor the names of its contributors may
   be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

bl_info = {
    "name": "OurBricks for Blender",
    "description": "Utilities for interacting with OurBricks within Blender.",
    "author": "Katalabs Inc.",
    "version": (0,0,1),
    "blender": (2, 5, 7),
    "api": 31236, # FIXME what's the right value here?
    "location": "File > Import-Export",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

# To support reload properly, try to access a package var, if it's there, reload everything
if "bpy" in locals():
    import imp

import os
import bpy
try:
    from bpy_extras.io_utils import ImportHelper
except:
    from io_utils import ImportHelper
from bpy.props import CollectionProperty, StringProperty, BoolProperty, FloatProperty

import zipfile, shutil, os.path
import urllib.request

class OurBricksImport(bpy.types.Operator):

    bl_idname = "import_scene.ourbricks_collada"
    bl_description = 'Import directly from OurBricks COLLADA'
    bl_label = "Import OurBricks"

    def invoke(self, context, event):
        url = context.scene.ourbricks_model_url

        # We piggy back on the standard COLLADA importer
        print('Importing', url)

        # Extract the unique asset id. FIXME this is brittle and
        # should be coming from some other listing, like a real API
        url_parts = url.split('/')
        unique_id_part = url_parts[ url_parts.index('processed')-1 ];

        # Make sure storage area exists.
        #
        # This storage area is necessary because things like textures
        # need to remain on disk. Here we just use a centralized
        # repository and take care to name things nicely.
        import_temp_dir = os.path.join('ourbricks', unique_id_part)
        if not os.path.exists(import_temp_dir): os.makedirs(import_temp_dir)

        # Grab data
        path = os.path.join(import_temp_dir, 'foo.zip')
        urllib.request.urlretrieve(url, filename=path, reporthook=None)

        # Extract data into a temporary location
        zipdata = zipfile.ZipFile(path)
        zipdata.extractall(path=import_temp_dir)

        # Find the collada file
        daes = [x for x in zipdata.namelist() if x.endswith('.dae')]
        if len(daes) != 1:
            # FIXME present choice in > 1 case, use real exception
            raise RuntimeError("Found zero or more than one dae.")
        dae_path = os.path.join(import_temp_dir, daes[0])

        # Perform the import
        bpy.ops.wm.collada_import(filepath=dae_path)

        return {'FINISHED'}

class OurBricksBrowserPanel(bpy.types.Panel):
    '''An interface for browsing and importing OurBricks content.'''

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "OurBricks Browser"

    def draw(self, context):
        row = self.layout.row()
        row.prop(context.scene, "ourbricks_model_url")
        row = self.layout.row()
        row.operator("import_scene.ourbricks_collada", text="Import")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.ourbricks_model_url = StringProperty(default="", name="URL", description="URL of model to import")

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.ourbricks_model_url

if __name__ == "__main__":
    register()
