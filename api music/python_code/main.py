import asyncio
import vlc
from music import multiplayer_web
from fastapi import FastAPI

musicas_to_reproduce = ['bones', 'reality', 'nobody']

# Sintaxis estandar de LibVLC sin comillas internas conflictivas
icecst = '#transcode{vcodec=none,acodec=mp3,ab=128,channels=2,samplerate=44100}:std{access=shout,mux=mp3,dst=source:hackme@icecast:8000/stream.mp3}'

yt = multiplayer_web(names=musicas_to_reproduce, icecast_instan=icecst)
inicio = 0
final = len(musicas_to_reproduce)
en_vivo = True
task_vivo = None


async def stream_music():
    global inicio, final, en_vivo
    en_vivo = True
    try:
        while en_vivo and 0 <= inicio < final:
            nombre_cancion = musicas_to_reproduce[inicio]
            exito = yt.reproductor_de_musica(nombre_cancion)

            if not exito:
                inicio += 1
                if inicio >= final:
                    inicio = 0
                continue

            await asyncio.sleep(3)

            # Mantenemos la ejecucion MIENTRAS VLC este reproduciendo
            while en_vivo and yt.player.get_state() in [vlc.State.Playing, vlc.State.Opening, vlc.State.Buffering]:
                await asyncio.sleep(0.5)

            if en_vivo and yt.player.get_state() in [vlc.State.Ended, vlc.State.Error, vlc.State.Stopped]:
                inicio += 1
                if inicio >= final:
                    inicio = 0

    except Exception as e:
        print(f"[stream_music Exception]: {e}")
    en_vivo = False


app = FastAPI(root_path="/api")


@app.post('/bienvenido')
async def inicia_cancion():
    global task_vivo, inicio
    if task_vivo and not task_vivo.done():
        task_vivo.cancel()
    yt.player.stop()
    inicio = 0
    task_vivo = asyncio.create_task(stream_music())
    return {"status": "ok", "message": "Iniciando reproduccion"}


@app.post('/stop')
def stop_music():
    global en_vivo, task_vivo
    en_vivo = False
    yt.player.stop()
    if task_vivo and not task_vivo.done():
        task_vivo.cancel()
    return {"status": "ok", "message": "Detenido"}


@app.post('/siguiente')
async def next_music():
    global inicio, task_vivo
    if inicio != final - 1:
        inicio += 1
    else:
        inicio = 0

    if task_vivo and not task_vivo.done():
        task_vivo.cancel()
    yt.player.stop()
    task_vivo = asyncio.create_task(stream_music())
    return {"status": "ok", "message": f"Siguiente pista {inicio}"}


@app.post('/anterior')
async def previous_music():
    global inicio, task_vivo
    if inicio != 0:
        inicio -= 1
    else:
        inicio = 0

    if task_vivo and not task_vivo.done():
        task_vivo.cancel()
    yt.player.stop()
    task_vivo = asyncio.create_task(stream_music())
    return {"status": "ok", "message": f"Anterior pista {inicio}"}


@app.post('/pausar_reanudar')
def pausa_reanudar():
    if yt.player.is_playing():
        yt.player.pause()
        return {"status": "ok", "message": "Pausado"}
    else:
        yt.player.play()
        return {"status": "ok", "message": "Reanudado"}