import os
import discord, asyncio
from discord.ext import commands
from keep_alive import keep_alive

# Configuración
TOKEN = 'Token-aca-here-oi-nosew'
PREFIX = '+'

# Obtener la ruta completa de la carpeta actual
carpeta_actual = os.getcwd()

carpetas_mp3 = {
    "test1": os.path.join(carpeta_actual, "test1"),
    "test2": os.path.join(carpeta_actual, "test2")
}

cola_de_reproduccion = []
cancion_actual = None

# Inicializar el bot
intents = discord.Intents.all()
intents.voice_states = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

def obtener_archivos_mp3_en_carpetas():
  archivos_por_carpeta = {}
  for nombre_carpeta, ruta_carpeta in carpetas_mp3.items():
      archivos_en_carpeta = [file for file in os.listdir(ruta_carpeta) if file.endswith(".mp3")]
      archivos_por_carpeta[nombre_carpeta] = archivos_en_carpeta
  return archivos_por_carpeta

# Función para obtener el nombre de la canción sin la extensión de archivo
def obtener_nombre_cancion(mp3_file):
  return os.path.splitext(mp3_file)[0]

# Comando para listar carpetas y archivos MP3 disponibles
@bot.command()
async def lista(ctx):
  print("Comando lista ejecutado")  # Depuración

  # Obtener archivos MP3 disponibles en las carpetas
  archivos_por_carpeta = obtener_archivos_mp3_en_carpetas()

  # Crear embed
  embed = discord.Embed(title="Carpetas y archivos MP3 disponibles")
  for nombre_carpeta, archivos in archivos_por_carpeta.items():
      if archivos:
          embed.add_field(name=nombre_carpeta, value="\n".join(archivos), inline=False)
      else:
          embed.add_field(name=nombre_carpeta, value="No hay archivos MP3 en esta carpeta.", inline=False)

  await ctx.send(embed=embed)

# Función para obtener el nombre de la canción sin la extensión de archivo
def obtener_nombre_cancion(mp3_file):
    return os.path.splitext(mp3_file)[0]

# Función para reproducir la próxima canción en la cola de reproducción
async def reproducir_proxima_cancion(ctx):
    global cancion_actual, cola_de_reproduccion
    if cola_de_reproduccion:
        voice_client = ctx.voice_client
        if not voice_client:
            voice_channel = ctx.author.voice.channel
            voice_client = await voice_channel.connect()
        siguiente_cancion = cola_de_reproduccion.pop(0)
        cancion_actual = obtener_nombre_cancion(os.path.basename(siguiente_cancion))
        voice_client.play(discord.FFmpegPCMAudio(siguiente_cancion), after=lambda e: asyncio.run(reproducir_proxima_cancion(ctx)))

# Comando para agregar una canción a la cola de reproducción
@bot.command()
async def next(ctx, carpeta, *, mp3_file):
    carpeta = carpeta.lower()
    if carpeta not in carpetas_mp3:
        await ctx.send("¡La carpeta especificada no existe!")
        return
    mp3_path = os.path.join(carpetas_mp3[carpeta], mp3_file)
    cola_de_reproduccion.append(mp3_path)
    await ctx.send(f"La canción {obtener_nombre_cancion(mp3_file)} ha sido agregada a la cola de reproducción.")
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        await reproducir_proxima_cancion(ctx)

# Comando para reproducir una canción desde la cola de reproducción o desde un archivo especificado
@bot.command()
async def play(ctx, carpeta=None, *, mp3_file=None):
    global cancion_actual
    if ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.send("Ya se está reproduciendo una canción.")
        return
    if carpeta and mp3_file:
        carpeta = carpeta.lower()
        if carpeta not in carpetas_mp3:
            await ctx.send("¡La carpeta especificada no existe!")
            return
        mp3_path = os.path.join(carpetas_mp3[carpeta], mp3_file)
        if not os.path.exists(mp3_path):
            await ctx.send("¡No se encontró el archivo MP3!")
            return
        cola_de_reproduccion.append(mp3_path)
        cancion_actual = obtener_nombre_cancion(mp3_file)
    await reproducir_proxima_cancion(ctx)

# Comando para detener la reproducción de una canción y limpiar la cola de reproducción
@bot.command()
async def stop(ctx):
    global cancion_actual, cola_de_reproduccion
    if ctx.voice_client:
        ctx.voice_client.stop()
        cola_de_reproduccion.clear()
        cancion_actual = None
        await ctx.voice_client.disconnect()

# Comando para saltar a la siguiente canción en la cola de reproducción
@bot.command()
async def skip(ctx):
    global cancion_actual, cola_de_reproduccion
    if ctx.voice_client:
        ctx.voice_client.stop()
    if cola_de_reproduccion:
        siguiente_cancion = cola_de_reproduccion.pop(0)
        cancion_actual = obtener_nombre_cancion(os.path.basename(siguiente_cancion))
        await reproducir_proxima_cancion(ctx)
    else:
        await ctx.send("¡No hay canciones en la cola de reproducción!")

# Comando para mostrar la cola de reproducción
@bot.command()
async def queue(ctx):
    global cancion_actual, cola_de_reproduccion
    embed = discord.Embed(title="Cola de Reproducción")
    if cancion_actual:
        embed.add_field(name="Reproduciendo ahora:", value=cancion_actual, inline=False)
    else:
        embed.add_field(name="Reproduciendo ahora:", value="No hay canciones en reproducción", inline=False)
    if cola_de_reproduccion:
        nombres_canciones = [obtener_nombre_cancion(os.path.basename(cancion)) for cancion in cola_de_reproduccion]
        embed.add_field(name="Próximas canciones:", value="\n".join(nombres_canciones), inline=False)
    else:
        embed.add_field(name="Próximas canciones:", value="No hay canciones en cola de reproducción", inline=False)
    await ctx.send(embed=embed)

#Comando de prueba
@bot.command()
async def hello(ctx):
    await ctx.send("Hello, I am a robot")

# Ejecutar el bot
bot.run(TOKEN)
