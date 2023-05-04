import sounddevice as sd
from laptop_speech import KeywordRecognizer
from laptop_speech import SpeechPublisher, ButtonListener

if __name__ == "__main__":
    import config

    DEBUG_MIC = True
    special_words = config.SPECIAL_WORDS
   
    print(sd.query_devices(1))
    print(sd.query_devices(2))

    spub1 = SpeechPublisher("ECE180/Team1/speech/p1")
    blis1 = ButtonListener("ECE180/Team1/button/p1")

    spub2 = SpeechPublisher("ECE180/Team1/speech/p2")
    blis2 = ButtonListener("ECE180/Team1/button/p2")

    try:
        myrec_p1 = KeywordRecognizer(1, special_words)
        myrec_p2 = KeywordRecognizer(2, special_words)
        while True:
            # Get the top of the queue and pass through our recognizer
            d = myrec_p1.get_data()
            d2 = myrec_p2.get_data()
            new_p1, word_p1 = myrec_p1.test_data(d, True)
            new_p2, word_p2 = myrec_p2.test_data(d2, True)
            if (blis1.button_active(1) or DEBUG_MIC) and new_p1:
                print(f"PLAYER 1: NEW: {new_p1} \t WORD: {word_p1}")
                spub1.publish(word_p1)
            if (blis2.button_active(1) or DEBUG_MIC) and new_p2: 
                print(f"PLAYER 2: NEW: {new_p2} \t WORD: {word_p2}")
                spub2.publish(word_p2)
    
    except (KeyboardInterrupt, EOFError):
        print('Received KeyboardInterrupt')