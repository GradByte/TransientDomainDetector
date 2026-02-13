import websocket

def on_message(ws, message):
    print(f"Received: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

def on_open(ws):
    print("Connection opened")

# Enable trace for debugging
websocket.enableTrace(True)

# Create WebSocket connection
ws = websocket.WebSocketApp(
    "wss://zonestream.openintel.nl/ws/newly_registered_domain",
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
    on_open=on_open
)

# Run the WebSocket connection
ws.run_forever()