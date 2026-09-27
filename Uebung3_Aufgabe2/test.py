import keyboard

while True:
    if keyboard.read_key == "35":
        print("Ctrl + P pressed")
        break
    print(keyboard.read_key())

# sequence = []
# expected_sequence = ['ctrl', 'p', 'ctrl', 'd']

# def on_key_event(event):
#     global sequence
#     name = event.name

#     # Normalize 'left ctrl' and 'right ctrl' to 'ctrl'
#     if name in ('left ctrl', 'right ctrl'):
#         name = 'ctrl'

#     # Only consider 'down' events to avoid duplicates
#     if event.event_type == 'down':
#         sequence.append(name)
#         print(f"Key pressed: {name}")
#         print(f"Current sequence: {sequence}")

#         # Check if the current sequence matches the expected sequence
#         if sequence == expected_sequence:
#             print("Trigger activated! Sending text...")
#             return False  # Stop listener

#         # Reset sequence if it doesn't match the expected start
#         if expected_sequence[:len(sequence)] != sequence:
#             sequence = []

# # Start listening to key events
# keyboard.hook(on_key_event)

# print("Press Ctrl+P and then Ctrl+D to trigger the message.")
# keyboard.wait()  # Wait indefinitely until the listener is stopped
