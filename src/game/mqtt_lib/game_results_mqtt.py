import paho.mqtt.client as mqtt

class GameResultsMQTT():
    def __init__(self, topic: str="game_results/local"):
        self.topic = topic

        # initialize MQTT values
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.connect_async('mqtt.eclipseprojects.io')
        self.client.loop_start()

        # contains score from opponent game
        self.team_1_score = 0
        self.team_2_score = 0

        self.total_scores_receieved = 0

    def publish_my_score(self, teamID, my_score):
        message = str(teamID) + "," + str(my_score)
        self.client.publish(self.topic, message, qos=1)

    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic, qos=1)
    
    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print('Unexpected Disconnect')
        else:
            print('Expected Disconnect')

    # on message, should be receiving opponent game's score
    def _on_message(self, client, userdata, message):
        msg = message.payload.decode()
        teamID, score = msg.split(',')

        teamID = int(teamID)
        score = int(score)
        
        if teamID == 1:
            self.team_1_score = score
        elif teamID == 2:
            self.team_2_score = score
        
        self.total_scores_receieved += 1