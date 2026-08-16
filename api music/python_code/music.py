import os
import requests
import yt_dlp
import vlc

class multiplayer_web(object):
    def __init__(self, names: list, icecast_instan: str):
        self.names = names
        self.icecast_instan = icecast_instan
        self.vlc_instance = vlc.Instance(
            '--aout=adummy',
            '--no-video',
            '--http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            '--verbose=1'
        )
        self.player = self.vlc_instance.media_player_new()

    def buscador_de_musica(self, name: str):
        p = {
            'format': 'bestaudio[protocol=http]/bestaudio',
            'quiet': True,
            'no_warnings': True,
        }
        try:
            with yt_dlp.YoutubeDL(p) as f:
                info = f.extract_info(f'scsearch1:{name}', download=False)
                url_directa = info['entries'][0]['url']

            # Descargar el archivo completo a un temporal en vez de streamear la URL directa
            respuesta = requests.get(url_directa, timeout=15)
            respuesta.raise_for_status()

            ruta_local = f"/tmp/{name.replace(' ', '_')}.mp3"
            with open(ruta_local, 'wb') as archivo:
                archivo.write(respuesta.content)

            return ruta_local
        except Exception as e:
            print(f"[buscador_de_musica] Error buscando '{name}': {e}")
            return None

    def reproductor_de_musica(self, music_name: str):
        ruta_local = self.buscador_de_musica(music_name)
        if not ruta_local:
            print(f"--> [Error] No se pudo obtener el audio de: {music_name}")
            return False

        print(f"--> [VLC] Transmitiendo hacia Icecast: {music_name}")
        media = self.vlc_instance.media_new(ruta_local)
        media.add_option(f':sout={self.icecast_instan}')
        media.add_option(':network-caching=5000')
        self.player.set_media(media)
        self.player.play()
        return True
