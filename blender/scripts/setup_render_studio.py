"""
not.know.archive — Setup Render Studio
Motor: Cycles | Resolución: 8K | Iluminación: ventana lateral (Jil Sander)
Ejecutar desde: Blender > Scripting > Run Script
"""

import bpy
import math


# ─────────────────────────────────────────────
# 01. MOTOR DE RENDER — CYCLES 8K
# ─────────────────────────────────────────────

scene = bpy.context.scene

# Motor
scene.render.engine = 'CYCLES'

# Dispositivo (GPU si disponible, CPU como fallback)
cycles = scene.cycles
cycles.device = 'GPU'

# Resolución 8K
scene.render.resolution_x = 7680
scene.render.resolution_y = 4320
scene.render.resolution_percentage = 100

# Calidad de muestreo
cycles.samples = 512
cycles.use_denoising = True
cycles.denoiser = 'OPENIMAGEDENOISE'

# Profundidad de color y formato de salida
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_depth = '16'
scene.render.image_settings.color_mode = 'RGB'

# Path de salida por defecto
scene.render.filepath = "//renders/8K_master_"

print("[not.know.archive] Cycles 8K configurado.")


# ─────────────────────────────────────────────
# 02. LIMPIEZA — eliminar luces existentes
# ─────────────────────────────────────────────

for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)

print("[not.know.archive] Luces anteriores eliminadas.")


# ─────────────────────────────────────────────
# 03. ILUMINACIÓN — VENTANA LATERAL (JIL SANDER)
#
# Concepto: luz natural difusa desde la izquierda,
# como una ventana grande de estudio. Sombras suaves
# y controladas. Sin flash, sin dramatismo — solo
# la verdad del material.
# ─────────────────────────────────────────────

def add_area_light(name, location, rotation_deg, size_x, size_y, energy, color=(1.0, 0.98, 0.95)):
    bpy.ops.object.light_add(type='AREA', location=location)
    light_obj = bpy.context.active_object
    light_obj.name = name
    light_obj.rotation_euler = [math.radians(r) for r in rotation_deg]

    light_data = light_obj.data
    light_data.shape = 'RECTANGLE'
    light_data.size = size_x
    light_data.size_y = size_y
    light_data.energy = energy
    light_data.color = color
    light_data.use_shadow = True
    light_data.cycles.use_multiple_importance_sampling = True

    return light_obj


# VENTANA PRINCIPAL — lateral izquierda
# Grande, difusa, ligeramente inclinada hacia el objeto
add_area_light(
    name="LUZ_VENTANA_PRINCIPAL",
    location=(-2.5, 0.0, 1.5),
    rotation_deg=(0, -75, 90),
    size_x=2.0,
    size_y=3.0,
    energy=600,
    color=(1.0, 0.97, 0.93)   # luz de día fría-cálida, sin amarillo
)

# RELLENO SUAVE — derecha, muy bajo
# Solo para que el material no caiga en negro absoluto
add_area_light(
    name="LUZ_RELLENO",
    location=(2.0, 0.5, 0.8),
    rotation_deg=(0, 60, -90),
    size_x=1.5,
    size_y=2.0,
    energy=80,
    color=(0.95, 0.97, 1.0)   # relleno frío, contrasta con la principal
)

# CONTRALUZ — detrás-arriba
# Define el borde del objeto, separa del fondo
add_area_light(
    name="LUZ_CONTRALUZ",
    location=(0.0, -2.0, 2.5),
    rotation_deg=(-45, 0, 180),
    size_x=1.0,
    size_y=0.5,
    energy=120,
    color=(1.0, 1.0, 1.0)
)

print("[not.know.archive] Iluminación de estudio aplicada: ventana lateral + relleno + contraluz.")


# ─────────────────────────────────────────────
# 04. FONDO — gris neutro estructural
# ─────────────────────────────────────────────

world = scene.world
if world is None:
    world = bpy.data.worlds.new("World_notknow")
    scene.world = world

world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.12, 0.12, 0.12, 1.0)  # gris oscuro neutro
    bg_node.inputs[1].default_value = 0.0                         # sin emisión de entorno

print("[not.know.archive] Fondo neutro configurado.")


# ─────────────────────────────────────────────
# 05. RESUMEN DE CONFIGURACIÓN
# ─────────────────────────────────────────────

print("\n─── not.know.archive / ESTUDIO LISTO ───")
print(f"  Motor:        {scene.render.engine}")
print(f"  Resolución:   {scene.render.resolution_x} × {scene.render.resolution_y}")
print(f"  Samples:      {cycles.samples}")
print(f"  Luces:        {[o.name for o in bpy.data.objects if o.type == 'LIGHT']}")
print("────────────────────────────────────────\n")


# ─────────────────────────────────────────────
# 06. GUARDAR
# ─────────────────────────────────────────────

bpy.ops.wm.save_mainfile()
print("[not.know.archive] Archivo guardado.")
