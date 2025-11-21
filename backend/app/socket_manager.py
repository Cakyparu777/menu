import socketio

# Create a Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# Wrap with ASGI application
app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def join_room(sid, room):
    """
    Allow clients to join a specific room (e.g., 'restaurant_1')
    to receive updates for that context.
    """
    print(f"Client {sid} joining room: {room}")
    sio.enter_room(sid, room)

async def notify_new_order(restaurant_id, order_data):
    """
    Emit a 'new_order' event to the specific restaurant room.
    """
    await sio.emit('new_order', order_data, room=f'restaurant_{restaurant_id}')

async def notify_order_update(order_id, status, customer_id=None):
    """
    Emit an 'order_update' event.
    If customer_id is provided, we could target a specific user room,
    but for now we'll broadcast to the restaurant room or a global updates channel.
    """
    # For simplicity, we might just broadcast to the restaurant room for now
    # In a real app, we'd have user-specific rooms.
    pass
