import logging
import os
import sys
import queue
import threading
import sounddevice as sd
import soundfile as sf
import pygame


DEFAULT_SONG_FOLDER = os.path.abspath("songs")

def list_songs(song_folder=None):
    """ List the parsed songs in the specified folder """
    song_folder = DEFAULT_SONG_FOLDER if song_folder is None else song_folder
    return [parse_song_filename(n) for n in os.listdir(song_folder)]
  
def parse_song_filename(song_filename):
    """ 
    Parse the filename of the song to get the relevant information from 
    the filename 
    """
    split_file = song_filename.split("--")
    artist = " ".join(split_file[0].split("_"))
    title = " ".join(split_file[1].split("_"))
    bpm = int(split_file[2].split("bpm")[0])
    
    return {"artist": artist, "title": title, "bpm": bpm, "filename": song_filename}

def get_from_title(song_list, title):
    for s in song_list: 
        if s["title"] == title:
            return s
    logging.warning("MUSIC: Title does not exist in song_list")
    raise RuntimeError

class MusicSelector:
    song_list = list_songs()

    def __init__(self, title, song_folder=None, difficulty=None) -> None:
        logging.debug("MUSIC: Initializing")

        self.difficulty = difficulty

        song = get_from_title(song_list, title)
        self.artist = song["artist"]
        self.title = song["title"]
        self.bpm = song["bpm"]
        self.filename = song["filename"]

        self.path = os.path.join(song_folder if song_folder is not None else DEFAULT_SONG_FOLDER, self.filename)
        logging.debug(f"MUSIC: path set to {self.path}")
        
        self.buffer_size = 20
        self.block_size = 2048
        self.q = queue.Queue(maxsize=self.buffer_size)
        self.event = threading.Event()

    def play_song(self, device):
        try:
            with sf.SoundFile(self.path) as f:
                for _ in range(self.buffer_size):
                    data = f.read(self.block_size)
                    if not len(data):
                        break
                    self.q.put_nowait(data)  # Pre-fill queue
                stream = sd.OutputStream(
                    samplerate=f.samplerate, blocksize=self.block_size,
                    device=device, channels=f.channels,
                    callback=self.callback)#, finished_callback=self.event.set)
                with stream:
                    timeout = self.block_size * self.buffer_size / f.samplerate
                    while len(data):
                        data = f.read(self.block_size)
                        self.q.put(data, timeout=timeout)
                    # self.event.wait()  # Wait until playback is finished
        except KeyboardInterrupt:
            sys.exit('\nInterrupted by user')
        except queue.Full:
            # A timeout occurred, i.e. there was an error in the callback
            sys.exit(1)
        except Exception as e:
            sys.exit(type(e).__name__ + ': ' + str(e))
    

    def callback(self, outdata, frames, time, status):
        assert frames == self.block_size
        if status.output_underflow:
            print('Output underflow: increase blocksize?', file=sys.stderr)
            raise sd.CallbackAbort
        assert not status
        try:
            data = self.q.get_nowait()
        except queue.Empty as e:
            print('Buffer is empty: increase buffersize?', file=sys.stderr)
            raise sd.CallbackAbort from e
        if len(data) < len(outdata):
            outdata[:len(data)] = data
            outdata[len(data):].fill(0)
            raise sd.CallbackStop
        else:
            outdata[:] = data

    def __repr__(self):
        return f"TITLE: {self.title}, ARTIST: {self.artist}, BPM: {self.bpm}"

class MusicPlayer():

    def __init__(self, title, song_folder=None, difficulty=None) -> None:
        logging.debug("MUSIC: Initializing")

        self.difficulty = difficulty

        song = get_from_title(song_list, title)
        self.artist = song["artist"]
        self.title = song["title"]
        self.bpm = song["bpm"]
        self.filename = song["filename"]

        self.path = os.path.join(song_folder if song_folder is not None else DEFAULT_SONG_FOLDER, self.filename)
        logging.debug(f"MUSIC: path set to {self.path}")
        pygame.mixer.init()
        pygame.mixer.music.load(self.path)
    
    def play_song(self):
        pygame.mixer.music.play()


if __name__ == "__main__": 
    # logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    
    print("Beginning to music test script")

    parsed = parse_song_filename(os.listdir(DEFAULT_SONG_FOLDER)[0])
    print(parsed)

    song_list = list_songs()
    print(song_list)

    ms_song_filename = get_from_title(song_list, "I Gotta Feeling")
    print(f"here is the filename: {ms_song_filename}")

    print()
    ms = MusicPlayer("I Gotta Feeling")
    logging.info(ms)

    # Currently blocks when playing the song. Need to find a way to play in the background
    # Investigating the python multiprocessing library
    ms.play_song()
    logging.debug("In main")
    
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)