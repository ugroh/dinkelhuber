# Dinkelhuber, a browser based 9x9 OGS Go Opening explorer with Katago support
![Site preview](/images/site_preview.png)
## Check it out now
Dinkelhuber is a purely browser based 9x9 Go client and opening explorer that you can visit at [go.yannikkeller.de](http://go.yannikkeller.de).
## Features
### Opening explorer
In the tab on the right, you can explore over 400k [OGS](https://online-go.com/) games, exploring the number of games, winrates for black and white and the average rating of the players of each move. By clicking on the cogwheel in the top-right, you can also filter the games for rules, komi or player strength. Below the moves on the right, you will find a list of top [OGS](https://online-go.com/) games played in the line, which you can easily reach by clicking on them. Note that the ratings might not always perfectly match with the ones shown at [OGS](https://online-go.com/), but that's caused by the way [OGS](https://online-go.com/) handles ratings and rating change.
### Exploring OGS games
You can directly import [OGS](https://online-go.com/) games to dinkelhuber. Just visit your game on [OGS](https://online-go.com/), copy the Game ID from the end of the URL, enter it into dinkelhuber's Game ID input field, hit enter, and the use the arrow keys to navigate through the game.
### Running Katago
The browser go client can show engine lines in [lizzie](https://github.com/featurecat/lizzie) style. Of course, as I am not rich, I can't provide free [katago](https://github.com/lightvector/KataGo) analysis from my server, so you will have to run [katago](https://github.com/lightvector/KataGo) on your own machine. To get going, first make sure, that you have a working [katago](https://github.com/lightvector/KataGo) on a Linux machine (No Windows support yet). Then clone this repository. Navigate to [python_server/gtp_socket_wrapper](python_server/gtp_socket_wrapper) and create a folder `katago` where you put your katago executable as well as your `default_gtp.cfg` and `default_model.bin.gz` in. You will need Python 3 with the websock package installed `pip3 install websock`. Now start a terminal in `python_server/gtp_socket_wrapper` and run `python3 websocket_server.py`. In a browser navigate to [go.yannikkeller.de](http://go.yannikkeller.de) and enter `localhost:8030` into the GTP engine field and hit enter. If everything worked correctly, you should see engine evaluations plopping up on the board after a few seconds.

The neat thing about running katago via a websocket is that you can also access your katago instance remotely via your local network or even via the internet (If you have a good understanding of networking and sockets). To do this, you will need to edit the ip in `server = WebSocketServer(ip="localhost", port=8030,` in [websocket_server.py](python_server/gtp_socket_wrapper/websocket_server.py) to your machines network ip and then you can access it via this ip from your phone for example.

## Acknowledgements
Thanks [OGS](https://online-go.com/) for providing such a nice and easy game downloading api, without which dinkelhuber would not be possible.  
Thanks to [lichess](https://lichess.org/) the forever free and awesome chess platform, I got my opening explorer design from.  
Thanks to [kocsten](https://codepen.io/kocsten) for some awesome button designs.