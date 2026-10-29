"""OBJ/3DS → GLB with Blender."""
import os, sys
import bpy
args = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
if len(args) < 2:
    print("usage: -- <in.obj|in.3ds> <out.glb>"); raise SystemExit(2)
src, dst = args[0], args[1]
ext = os.path.splitext(src)[1].lower()
target = None
for i, a in enumerate(args):
    if a == "--target" and i + 1 < len(args):
        target = float(args[i + 1])
bpy.ops.wm.read_factory_settings(use_empty=True)
try:
    if ext == ".obj":
        bpy.ops.wm.obj_import(filepath=src)
    else:
        bpy.ops.import_scene.autodesk_3ds(filepath=src)
except Exception as e:
    print("import fail:", e); raise SystemExit(3)
# archive3d 模型單位不一致（mm / cm / m 混用），統一縮到指定實際尺寸
if target:
    import mathutils
    lo = mathutils.Vector((1e18,)*3); hi = mathutils.Vector((-1e18,)*3)
    for ob in bpy.context.scene.objects:
        if ob.type != "MESH": continue
        for c in ob.bound_box:
            w = ob.matrix_world @ mathutils.Vector(c)
            for i in range(3):
                lo[i] = min(lo[i], w[i]); hi[i] = max(hi[i], w[i])
    biggest = max((hi - lo)[:])
    if biggest > 0:
        k = target / biggest
        for ob in bpy.context.scene.objects:
            ob.location *= k
            ob.scale *= k
        bpy.context.view_layer.update()
        print(f"scaled x{k:.5f} (was {biggest:.1f} units -> {target} m)")

meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
tris=0
for ob in meshes:
    ob.data.calc_loop_triangles(); tris += len(ob.data.loop_triangles)
for img in bpy.data.images:
    if img.name=="Render Result" or img.packed_file or not img.filepath: continue
    try: img.pack()
    except Exception: pass
os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", export_apply=True,
                          export_yup=True, export_materials="EXPORT", export_image_format="AUTO")
print("=== RESULT ===")
print(f"meshes    {len(meshes)}")
print(f"triangles {tris:,}")
print(f"glb       {dst}  ({os.path.getsize(dst)/1e6:.2f} MB)")
