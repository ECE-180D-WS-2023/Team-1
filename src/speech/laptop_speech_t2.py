import queue
import sys
import sounddevice as sd
import json
import logging
import paho.mqtt.client as mqtt
import time

from vosk import Model, KaldiRecognizer, SetLogLevel


# logging.basicConfig(filename='game.log', filemode='w',
#                     format='%(name)s - %(levelname)s - %(message)s')


class KeywordRecognizer():
    """
    A class to recognize the player's voice commands.
    NOTE: The `KeywordRecognizer` class must be contained within a `try except`
    statement. 

    ...

    Attributes
    ----------
    q : queue.Queue()
    special_words : dict
    model : Model
    rec : KaldiRecognizer
    prev_guess : str
    """

    def __init__(self, id: int, special_words: dict) -> None:
        self.q = queue.Queue()
        self.special_words = special_words

        # Turn off Vosk CLI logging feature (on by default)
        SetLogLevel(-1)

        # Initialize the Vosk Model
        self.model = Model(lang="en-us")

        # Set up the sound device to the first available input
        device_info = sd.query_devices(id)
        samplerate = int(device_info["default_samplerate"])

        self.mic = sd.RawInputStream(samplerate=samplerate, blocksize=8000,
                                     device=device_info["index"], dtype="int16",
                                     channels=1, callback=self.callback)
        # print("AAAA")
        self.mic.start()
        # print(self.mic)
        # Initialize the Recognizer
        self.rec = KaldiRecognizer(self.model, samplerate)
        self.prev_guess = ""

        logging.info("SPEECH: Starting the recognizer!")

    def __del__(self):
        """
        NOT IMPLEMENTED: Delete the object
        Might need this not sure yet
        """
        # self.mic.__exit__()
        # self.mic.stop()
        # self.mic.close()
        logging.info("SPEECH: Deleting the recognizer")

    def get_data(self):
        """Get the first value of the binary queue"""
        # print(self.q.get())
        return self.q.get()

    def clear_q(self):
        """Clear the audio bitsream queue"""
        # TODO test this function
        with self.q.mutex:
            self.q.queue.clear()
        logging.info("SPEECH: Cleared Queue")

    def test_data(self, data, verbose=False):
        """
        Check the value of the data and returns the most recent spoken command.

        Parameters
        ----------
        data : binarydata
        verbose : bool optional

        Returns
        --------
        new_word : bool
            `True` if there is a new word. `False` otherwise
        word : str
            The most recent new word. 
        """
        # If our recognizer completed it's prediction for the given phrase
        # it sets rec.AcceptWaveform to True and stores the result in
        # rec.Result
        # print(data)
        rtguess = ""
        if self.rec.AcceptWaveform(data):
            if verbose:
                print(f"Your model thought you said: {self.rec.Result()}")
                logging.debug(f"SPEECH: model thought you said: {self.rec.Result()}")
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
                        logging.debug(f"SPEECH: COMMAND {word} DETECTED!")
                        self.prev_guess = rtguess
                        return True, word
                self.prev_guess = rtguess

        return False, rtguess

    @staticmethod
    def print_sound_device(id):
        print(sd.query_devices(id))

    @staticmethod
    def print_all_sound_devices():
        # print(sd.query_devices())
        print(sd.query_devices(kind="input"))


    def callback(self, indata, frames, time, status):
        """
        Check for invalid status and add the indata to the queue.
        This is called (from a separate thread) for each audio block.
        """
        if status:
            print(status, file=sys.stderr)
            logging.error(f"SPEECH: ERROR {status}")

        self.q.put(bytes(indata))

   
class SpeechPublisher():

    def __init__(self, topic: str) -> None:
        self.topic = topic

        # initialize MQTT values
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.connect_async('mqtt.eclipseprojects.io')
        self.client.loop_start()
        self.client.publish(self.topic, 1, qos=1)

    def _on_message(self, client, userdata, message):
        msg_str = str(message.payload)[2]
        print(msg_str)

    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic, qos=1)
        print("Connection returned result: " + str(rc))
    
    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print('Unexpected Disconnect')
        else:
            print('Expected Disconnect')

    def publish(self, text: str) -> None:
        self.client.publish(self.topic, text, qos=1) # publish on MQTT

class ButtonListener():

    def __init__(self, topic: str) -> None:
        self.topic = topic

        # initialize MQTT values
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.connect_async('mqtt.eclipseprojects.io')
        self.client.loop_start()
        self.client.publish(self.topic, 1, qos=1)

        self.button_high = False
        self.end_timer = time.time()
        # print(f"INITIALIZED BUTTON at {self.end_timer}")

    def button_active(self, delay):
        """
        Does the same thing as getting button_high, but 
        includes a delay between end of button press and 
        continued processing
        """
        cur_time = time.time()

        if self.button_high:
            return True

        # print(cur_time-self.end_timer)
        if cur_time-self.end_timer <= delay:
            # print("DELAY")
            return True

        return False

    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic, qos=1)
        print("Connection returned result: " + str(rc))
    
    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print('Unexpected Disconnect')
        else:
            print('Expected Disconnect')

    # on message, just update the player_location that the game is using for localization
    def _on_message(self, client, userdata, message):
        msg_str = message.payload.decode() 
        # print(msg_str)

        if msg_str == "H":
            self.button_high = True
            # print("button High")
        elif msg_str == "L":
            self.button_high = False
            self.end_timer = time.time()
            # print(f"button Low {self.end_timer}")



if __name__ == "__main__":
    import config

    DEBUG_MIC = False
    special_words = config.SPECIAL_WORDS

    spub = SpeechPublisher("ECE180/Team2/speech")
    blis = ButtonListener("ECE180/Team2/button")

    KeywordRecognizer.print_all_sound_devices()
    KeywordRecognizer.print_sound_device(0)

    try:
        myrec = KeywordRecognizer(0, special_words)
        while True:
            # Get the top of the queue and pass through our recognizer
            d = myrec.get_data()
            new, word = myrec.test_data(d, True)
            if blis.button_high:
                print("button high")
            if (blis.button_high or DEBUG_MIC) and new:
                print(f"NEW: {new} \t WORD: {word} BUTTON: {blis.button_high}")
                spub.publish(word)
    
    except (KeyboardInterrupt, EOFError):
        print('Received KeyboardInterrupt')
