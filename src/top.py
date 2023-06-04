import os
import signal
import subprocess
import sys
import argparse
# from speech import laptop_speech
# from Localization import local_top


# Accept argument for the intial team number
parser = argparse.ArgumentParser()
parser.add_argument('-t', '--team',
                    help='The team number of the controller you wish to use',
                    required=False, default=1, type=int)
args = parser.parse_args()

try: 
    if args.team == 1:
        
        localization = subprocess.Popen([sys.executable, 'Localization/local_top.py']) #, 
                                            # stdout=subprocess.PIPE, 
                                            # stderr=subprocess.STDOUT)

        speech = subprocess.Popen([sys.executable, 'speech/laptop_speech.py']) #,
                                            # stdout=subprocess.PIPE, 
                                            # stderr=subprocess.STDOUT)
        game = subprocess.Popen([sys.executable, 'main.py']) #, 
                                            # stdout=subprocess.PIPE, 
                                            # stderr=subprocess.STDOUT)
        
        # os.system('python3 Localization/local_top.py')
        # os.system('python3 speech/laptop_speech.py')
        # os.system('python3 main.py')
    elif args.team == 2:
        print("TEAM 2")

    else:
       sys.exit("Invalid team number.") 
except KeyboardInterrupt:
    if args.team == 1:
        os.killpg(os.getpgid(localization.pid), signal.SIGTERM)  # Send the signal to all the process groups
        os.killpg(os.getpgid(speech.pid), signal.SIGTERM)  # Send the signal to all the process groups
        os.killpg(os.getpgid(game.pid), signal.SIGTERM)  # Send the signal to all the process groups

