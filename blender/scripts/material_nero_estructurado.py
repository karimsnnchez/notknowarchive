"""
not.know.archive — Material: Nero_Estructurado
Piel de grano fino, negro orgánico profundo, rugosidad realista.
Ejecutar desde: Blender > Scripting > Run Script
Requisito: tener una esfera (u objeto) seleccionado en la escena.
"""

import bpy


# ─────────────────────────────────────────────
# 01. OBTENER OBJETO SELECCIONADO
# ─────────────────────────────────────────────

obj = bpy.context.active_object

if obj is None or obj.type != 'MESH':
    raise Exception("[not.know.archive] ERROR: Selecciona una malla (mesh) antes de ejecutar.")

print(f"[not.know.archive] Objeto detectado: {obj.name}")


# ─────────────────────────────────────────────
# 02. CREAR MATERIAL
# ─────────────────────────────────────────────

mat_name = "Nero_Estructurado"

# Si ya existe, lo sobreescribimos
if mat_name in bpy.data.materials:
    bpy.data.materials.remove(bpy.data.materials[mat_name])

mat = bpy.data.materials.new(name=mat_name)
mat.use_nodes = True

nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

print("[not.know.archive] Material creado, árbol de nodos limpio.")


# ─────────────────────────────────────────────
# 03. NODOS — ÁRBOL COMPLETO
#
# Cadena:
# Noise (grano fino) → ColorRamp → Bump
# Voronoi (poros)    → ColorRamp ↗
# Principled BSDF → Material Output
# ─────────────────────────────────────────────

# Coordenadas de textura
tex_coord = nodes.new('ShaderNodeTexCoord')
tex_coord.location = (-1200, 0)

mapping = nodes.new('ShaderNodeMapping')
mapping.location = (-1000, 0)
mapping.inputs['Scale'].default_value = (8.0, 8.0, 8.0)   # escala del grano
links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])


# ── NOISE — grano superficial fino ──
noise_grain = nodes.new('ShaderNodeTexNoise')
noise_grain.location = (-760, 120)
noise_grain.inputs['Scale'].default_value = 18.0       # grano fino
noise_grain.inputs['Detail'].default_value = 12.0      # detalle alto
noise_grain.inputs['Roughness'].default_value = 0.65
noise_grain.inputs['Distortion'].default_value = 0.2
links.new(mapping.outputs['Vector'], noise_grain.inputs['Vector'])

# ColorRamp — convierte noise en variación de rugosidad sutil
ramp_grain = nodes.new('ShaderNodeValToRGB')
ramp_grain.location = (-520, 120)
ramp_grain.color_ramp.interpolation = 'EASE'
ramp_grain.color_ramp.elements[0].position = 0.35
ramp_grain.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)   # negro profundo
ramp_grain.color_ramp.elements[1].position = 0.75
ramp_grain.color_ramp.elements[1].color = (0.06, 0.04, 0.03, 1.0)  # negro cálido/orgánico
links.new(noise_grain.outputs['Fac'], ramp_grain.inputs['Fac'])


# ── VORONOI — poros de la piel ──
voronoi_pores = nodes.new('ShaderNodeTexVoronoi')
voronoi_pores.location = (-760, -180)
voronoi_pores.voronoi_dimensions = '3D'
voronoi_pores.distance = 'EUCLIDEAN'
voronoi_pores.inputs['Scale'].default_value = 28.0       # poros finos
voronoi_pores.inputs['Randomness'].default_value = 0.85
links.new(mapping.outputs['Vector'], voronoi_pores.inputs['Vector'])

# ColorRamp — poros como micro-depresiones para el bump
ramp_pores = nodes.new('ShaderNodeValToRGB')
ramp_pores.location = (-520, -180)
ramp_pores.color_ramp.interpolation = 'LINEAR'
ramp_pores.color_ramp.elements[0].position = 0.0
ramp_pores.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
ramp_pores.color_ramp.elements[1].position = 0.4
ramp_pores.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
links.new(voronoi_pores.outputs['Distance'], ramp_pores.inputs['Fac'])


# ── MIX — combinar grano + poros para el bump ──
mix_bump = nodes.new('ShaderNodeMixRGB')
mix_bump.location = (-280, 0)
mix_bump.blend_type = 'MULTIPLY'
mix_bump.inputs['Fac'].default_value = 0.6
links.new(ramp_grain.outputs['Color'], mix_bump.inputs['Color1'])
links.new(ramp_pores.outputs['Color'], mix_bump.inputs['Color2'])


# ── BUMP — relieve de la piel ──
bump = nodes.new('ShaderNodeBump')
bump.location = (-60, -60)
bump.inputs['Strength'].default_value = 0.55    # relieve presente pero no exagerado
bump.inputs['Distance'].default_value = 0.008   # micro-relieve
links.new(mix_bump.outputs['Color'], bump.inputs['Height'])


# ── NOISE ROUGHNESS — variación de rugosidad ──
# La piel no es uniforme: zonas más mate, zonas con micro-brillo
noise_rough = nodes.new('ShaderNodeTexNoise')
noise_rough.location = (-760, -420)
noise_rough.inputs['Scale'].default_value = 6.0
noise_rough.inputs['Detail'].default_value = 4.0
noise_rough.inputs['Roughness'].default_value = 0.5
links.new(mapping.outputs['Vector'], noise_rough.inputs['Vector'])

ramp_rough = nodes.new('ShaderNodeValToRGB')
ramp_rough.location = (-520, -420)
ramp_rough.color_ramp.elements[0].position = 0.0
ramp_rough.color_ramp.elements[0].color = (0.55, 0.55, 0.55, 1.0)   # roughness mínima
ramp_rough.color_ramp.elements[1].position = 1.0
ramp_rough.color_ramp.elements[1].color = (0.78, 0.78, 0.78, 1.0)   # roughness máxima
links.new(noise_rough.outputs['Fac'], ramp_rough.inputs['Fac'])


# ── PRINCIPLED BSDF — shader principal ──
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.location = (200, 0)

# Color base: negro orgánico, no puro — tiene profundidad
bsdf.inputs['Base Color'].default_value = (0.012, 0.009, 0.008, 1.0)

# Subsurface: mínimo, solo para que la piel "respire"
bsdf.inputs['Subsurface Weight'].default_value = 0.03
bsdf.inputs['Subsurface Scale'].default_value = 0.05
bsdf.inputs['Subsurface Color'].default_value = (0.08, 0.03, 0.01, 1.0)

# Especular y reflexión — la piel tiene brillo contenido, no plástico
bsdf.inputs['Specular IOR Level'].default_value = 0.18
bsdf.inputs['Roughness'].default_value = 0.68   # valor base, variado por noise

# Sheen — el micro-brillo característico de la piel
bsdf.inputs['Sheen Weight'].default_value = 0.12
bsdf.inputs['Sheen Roughness'].default_value = 0.5
bsdf.inputs['Sheen Tint'].default_value = (0.02, 0.015, 0.01, 1.0)

# Conectar roughness variable desde noise
links.new(ramp_rough.outputs['Color'], bsdf.inputs['Roughness'])

# Conectar bump a normal
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])


# ── MATERIAL OUTPUT ──
output = nodes.new('ShaderNodeOutputMaterial')
output.location = (480, 0)
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

print("[not.know.archive] Nodos de material configurados.")


# ─────────────────────────────────────────────
# 04. ASIGNAR MATERIAL AL OBJETO SELECCIONADO
# ─────────────────────────────────────────────

# Limpiar materiales anteriores del objeto
obj.data.materials.clear()
obj.data.materials.append(mat)

print(f"[not.know.archive] Material '{mat_name}' asignado a '{obj.name}'.")


# ─────────────────────────────────────────────
# 05. GUARDAR
# ─────────────────────────────────────────────

bpy.ops.wm.save_mainfile()

print("\n─── not.know.archive / NERO ESTRUCTURADO LISTO ───")
print(f"  Material:     {mat_name}")
print(f"  Objeto:       {obj.name}")
print(f"  Base Color:   Negro orgánico profundo (0.012, 0.009, 0.008)")
print(f"  Roughness:    0.55 – 0.78 (variable por noise)")
print(f"  Bump:         Grano fino + poros Voronoi")
print(f"  Sheen:        0.12 — micro-brillo de piel natural")
print("───────────────────────────────────────────────────\n")
