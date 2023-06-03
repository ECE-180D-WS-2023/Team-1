from .laptop_speech import *

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
            if (blis.button_active(1.0) or DEBUG_MIC) and new:
                print(f"NEW: {new} \t WORD: {word} BUTTON: {blis.button_high}")
                spub.publish(word)
    
    except (KeyboardInterrupt, EOFError):
        print('Received KeyboardInterrupt')
