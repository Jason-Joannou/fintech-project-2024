# How to get started

- Need to run the flask app using `python -m whatsapp-chatbot.src.server`. This will start the flask server with our whatsapp endpoint
- We then need to start the broker service by running `python -m whatsapp-chatbot.srv.start_broker`
- Then we need to run `ngrok http 5000` to create a secure tunnel to our local host
    - We need to use this ngrok address along with our endpoint (`ngrok_address/whatsapp`) in our twilio webhook on the twilio UI

Once all the above are running we can start sending messages to the twilio sandbox. 

This however is inconvinient for multiple reasons

- ngrok will regenerate an address everytime
- others can only use the ngrok tunnel if the person who created the tunnel, their pc remains running with the ngrok tunnel

We will have to heavily rely on TDD for the whatsapp chatbot, since we now what the incoming messages are, 

- incoming_msg: This represents what the user sent
- from_number: This represents the users number

We can create our functions based on these