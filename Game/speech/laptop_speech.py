import queue
import sys
import sounddevice as sd
import json

from vosk import Model, KaldiRecognizer, SetLogLevel

DEBUG = 1

class KeywordRecognizer():

    def __init__(self, id:int, special_words:dict) -> None:
        self.q = queue.Queue()
        self.special_words = special_words

        # Turn off Vosk CLI logging feature (on by default)
        SetLogLevel(-1)

        # Initialize the Vosk Model 
        self.model = Model(lang="en-us")

        # Set up the sound device to the first available input
        device_info = sd.query_devices(id)
        samplerate = int(device_info["default_samplerate"])

        self.mic = sd.RawInputStream(samplerate=samplerate, blocksize = 8000, 
                          device=device_info["name"], dtype="int16", 
                          channels=1, callback=self.callback)
        # print("AAAA")
        self.mic.start()
        print(self.mic)
        # Initialize the Recognizer
        self.rec = KaldiRecognizer(self.model, samplerate)
        self.prev_guess = ""

    def __del__(self):
        pass
        # self.mic.__exit__()
        # self.mic.stop()
        # self.mic.close()

    def get_data(self):
        # print(self.q.get())
        return self.q.get()

    def test_data(self, data):
        # If our recognizer completed it's prediction for the given phrase
        # it sets rec.AcceptWaveform to True and stores the result in 
        # rec.Result
        # print(data)
        if self.rec.AcceptWaveform(data):
            # print(f"Your model thought you said: {self.rec.Result()}")
            self.prev_guess = ""
        else:
            # Get the partial result string in the format of a json file.
            # Convert it to a json dict and get the value of "partial"
            rtguess = self.rec.PartialResult()
            rtguess = json.loads(rtguess)["partial"]

            # Only take the most recently said word in phrase
            if rtguess != "": 
                rtguess = rtguess.split()[-1]

            # Avoid recording multiple commands detected for the commands
            if rtguess != self.prev_guess:
                # print(f"GUESS: {rtguess} PREV: {self.prev_guess}")

                # Compare our real-time guess with our special words dict
                for word, errs in self.special_words.items():
                    if rtguess == word or rtguess in errs:
                        print(f"COMMAND {word} DETECTED!")
                        self.prev_guess = rtguess
                        return True, word
                self.prev_guess = rtguess

        return False, ""

    @staticmethod
    def print_sound_device(id):
        print(sd.query_devices(id))

    @staticmethod
    def print_all_sound_devices():
        print(sd.query_devices())

    def callback(self, indata, frames, time, status):
        """
        Check for invalid status and add the indata to the queue.
        This is called (from a separate thread) for each audio block.
        """
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))


if __name__ == "__main__":
    try:
        ####################################################################
        # Define the words that you want to detect in the format:
        # DESIRED_WORD : COMMON_ERROR_LIST
        # COMMON_ERROR_LIST is found experimentally using test_microphone.py
        #####################################################################
        # Make sure that all words in special_words are lowercase
        # and str type. The recognizer only outputs in lowercase
        #####################################################################
        special_words = {
            "start" : ["stuart", "stark"],
            "stop" : [],
            "pause" : [],
            "continue" : [],
            "player" : [],
            "enter": [],
            "one" : ["won"],
            "two" : ["to", "too"],
            "i'm excited" : ["i'm actually"],
        }

        KeywordRecognizer.print_all_sound_devices()
        KeywordRecognizer.print_sound_device(0)
        myrec = KeywordRecognizer(0, special_words)

        while True:
            # Get the top of the queue and pass through our recognizer
            # data = q.get()
            # print("here")
            d = myrec.get_data()
            new, word = myrec.test_data(d)
            if new:
                print(f"WORD: {word}")
    except (KeyboardInterrupt, EOFError):
        print('Received KeyboardInterrupt')
