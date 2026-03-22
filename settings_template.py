screen_resolution: int = 0 # No longer in use. Just here cause people are thoughtless.
base_path: str = None # No longer in use. Just here cause people are thoughtless.
lag_offset: float = 1.0
iguanadon: str = "GACHAIGUANADON1"
drop_off: str = "DEDIS01"
bed_spawn: str = "GACHARENDER1"
berry_station: str = "GACHABERRYSTATION1"
grindables: str = "GACHAGRINDABLES"
berry_type: str = "mejoberry"
station_yaw: float = -179.67
render_pushout: float = 166.74
external_berry: bool = False
height_ele: int = 3 
height_grind: int = 3
command_prefix: str = "%"
singleplayer: bool = False
server_number: str = 5502
crafting: bool = False
seeds_230: bool = False
game_platform: str = "Steam" # Change this to "Xbox" if using the Microsoft Store version or "Steam" if using the Steam Version
carcha_teleport: str = "CarchaMeatTeleport01" # The name of the teleporter next to Carcha before Ride
carcha_bed: str = "CarchaMeatBed02" # The name of the bed next to your Carcha


replicator_search_item: str = "tek ceiling" # Change this to whatever you are crafting
replicator_craft_amount: int = 20 # Number of times to press 'A'
replicator_slot: int = 1 # Crafting Slots (1-12)
megalab_slot: int = 7 # Crafting Slots (1-12)


# YOUR discord channel IDs and bot API key. To find channel IDs enable developer mode in discord and right click the channel to copy ID.
log_channel_gacha: int = 1478118074501824716
log_active_queue: int = 1478117785350701147
log_wait_queue: int = 1478117919169974273
discord_api_key: str = "YOUR_TOKEN_HERE"

startup_commands: str = "r.ScreenPercentage 100 | r.vsync 0 | t.MaxFPS 10 | r.Tonemapper.Sharpen 3 | r.VolumetricCloud 0 | r.VolumetricFog 0 | r.Fog 0 | r.SkyAtmosphere 0 | r.ShadowQuality 0 | r.Shadow.Virtual.Enable 0 | r.Shadow.CSM.MaxCascades 0 | r.ContactShadows 0 | r.DistanceFieldShadowing 0 | r.Lumen.Reflections.Allow 0 | r.Lumen.DiffuseIndirect.Allow 0 | r.Lumen.Reflections.Contrast 0 | r.Lumen.ScreenProbeGather.RadianceCache.ProbeResolution 128 | r.DynamicGlobalIlluminationMethod 0 | sg.GlobalIlluminationQuality 0 | r.Water.SingleLayer.Reflection 0 | r.SSR.Quality 0 | r.SkylightIntensityMultiplier 1 | r.LightShaftQuality 0 | r.LightCulling.Quality 0 | grass.SizeScale 0 | grass.DensityScale 0 | grass.Enable 0 | sg.FoliageQuality 0 | foliage.LODDistanceScale 0 | r.foliage.WPODisableMultiplier 1 | r.BloomQuality 0 | r.DepthOfFieldQuality 0 | r.MotionBlur.Amount 0 | r.EyeAdaptationQuality 0 | r.PostProcessing.DisableMaterials 1 | r.Color.Grading 1 | r.LensFlareQuality 2 | ark.MaxActiveDestroyedMeshGeoCollectionCount 0 | FX.MaxCPUParticlesPerEmitter 0 | fx.MaxNiagaraGPUParticlesSpawnPerFrame 0 | fx.EnableNiagaraSpriteRendering 0 | sg.EffectsQuality 0 | sg.TextureQuality 0 | r.MipMapLODBias 1 | r.Streaming.PoolSize 3000 | r.Nanite.MaxPixelsPerEdge 1 | wp.Runtime.HLOD 1 | r.DetailMode 0 | r.MaxAnisotropy 8 | r.FidelityFX.FSR3.Enabled 0 | r.FidelityFX.FSR3.UseNativeDX12 0 | r.VT.EnableFeedback 0 | r.AOOverwriteSceneColor 0 | Slate.GlobalScrollAmount 20 | stat fps | r.Water.SingleLayer 1 | r.Shading.FurnaceTest 0 | r.Shading.FurnaceTest.SampleCount 1 | r.SetNearClipPlane 10 | r.GlobalMinDirectionalLightAngle 0 | r.RefractionQuality 2 | r.TemporalAA 1"

if __name__ =="__main__":
    pass