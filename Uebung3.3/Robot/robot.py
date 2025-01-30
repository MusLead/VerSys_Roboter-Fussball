import paho.mqtt.client as mqtt
import argparse
from contextlib import contextmanager
import os
import signal
import sys
import threading
import grpc
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Controller')))

import robot_controller_pb2
import robot_controller_pb2_grpc

targetServer = os.getenv("TARGET_SERVER", "localhost")
BROKER = targetServer  # Replace with ActiveMQ broker's address
PORT = 1883  # Default MQTT port
TOPIC_ELECTION_ID = "leader_election_ID"  # Topic for leader election
TOPIC_ELECTION_REQUEST = "election_request"  # Topic for election request from the server
TOPIC_ONLINE = "online"  # Topic for online status
TOPIC_NUM_ONLINE = "num_online"  # Topic for number of online robots
TOPIC_ACK_LEADER = "ack_leader"  # Topic for acknowledging the leader
TOPIC_HI = "Hi_there"  # Topic for leader election

clients_messages = {}  # For storing messages for leader election
stub = None # gRPC stub instance
election_in_progress = False  # Flag to indicate if an election is in progress
amILeader = False # Flag to indicate if I am the leader
onlineLists = set() # Set to store online robots
onAckLists = set() # Set to store robots that acknowledged the leader
numRobots = 0 # Number of online robots
isError = False # Flag to indicate if the robot is in error state

INVALID_INPUT_MESSAGE = "Invalid input. Please write 'help' for further information."


# MQTT Listener
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"🤖 {userdata} connected successfully to ActiveMQ MQTT broker.")
        client.subscribe(TOPIC_ELECTION_REQUEST)
        client.subscribe(TOPIC_ELECTION_ID)
        client.subscribe(TOPIC_ACK_LEADER)
        client.subscribe(TOPIC_NUM_ONLINE)
        client.subscribe(TOPIC_ONLINE)
        client.subscribe(TOPIC_HI)
    else:
        print(f"🤖 {userdata} failed to connect. Return code {rc}")


def on_message(client, userdata, msg):
    global election_in_progress, amILeader
    message = msg.payload.decode()
    if isError:
        handle_error_message(userdata, msg, message)
        return
    if msg.topic == TOPIC_ELECTION_ID:
        handle_election_id_message(client, userdata, message, msg)
    elif msg.topic == TOPIC_ELECTION_REQUEST and not election_in_progress:
        handle_election_request_message(client, userdata, message, msg)
    elif msg.topic == TOPIC_ONLINE and amILeader:
        handle_online_message(client, message)
    elif msg.topic == TOPIC_NUM_ONLINE:
        handle_num_online_message(client, userdata)
    elif msg.topic == TOPIC_ACK_LEADER:
        handle_ack_leader_message(client, userdata, message, msg)
    elif msg.topic == TOPIC_HI:
        print(f"\n📡 Received message on topic '{msg.topic}': {message}\n🤖 {userdata} > ", end="")
    sys.stdout.flush()

def handle_error_message(userdata, msg, message):
    if msg.topic != TOPIC_ONLINE and msg.topic != TOPIC_NUM_ONLINE:
        print(f"\n📡 (ERROR) Received message on topic '{msg.topic}': {message}.\nNO ACTION WILL BE EXECUTED!\n🤖 {userdata} > ", end="")

def handle_election_id_message(client, userdata, message,msg):
    global clients_messages, election_in_progress
    print(f"\n📡 Received message on topic '{msg.topic}': {message}\n🤖 {userdata} > ", end="")
    other_robot_id, election_id = message.split(":")
    if other_robot_id != userdata:
        clients_messages[other_robot_id] = election_id  # Store these robot's election ID locally
    if userdata not in clients_messages and not election_in_progress:
        print("🔄 Userdata not found, triggering leader election...")
        elect_captain(stub, userdata, client)

def handle_election_request_message(client, userdata, message,msg):
    global election_in_progress
    print(f"\n📡 Received message on topic '{msg.topic}': {message}\n🤖 {userdata} > ", end="")
    while election_in_progress:
        time.sleep(1)
    elect_captain(stub, userdata, client)

def handle_online_message(client, message):
    global onlineLists, numRobots
    onlineLists.add(message)
    numRobots = len(onlineLists)
    client.publish(TOPIC_NUM_ONLINE, f"{numRobots}")

def handle_num_online_message(client, userdata):
    if not amILeader:
        if hasattr(client, 'leader_check_timer'):
            client.leader_check_timer.cancel()
        client.leader_check_timer = threading.Timer(2, elect_captain, args=(stub, userdata, client))
        client.leader_check_timer.start()
    else:
        if hasattr(client, 'leader_check_timer'):
            client.leader_check_timer.cancel()

def handle_ack_leader_message(client, userdata, message, msg):
    global onAckLists
    other_robot, my_id = message.split(":")
    if my_id == userdata:
        print(f"\n📡 Received message on topic '{msg.topic}': {message}\n🤖 {userdata} > ", end="")
        onAckLists.add(other_robot)
        if not hasattr(client, 'ack_check_thread') or not client.ack_check_thread.is_alive():
            client.ack_check_thread = threading.Thread(target=check_acknowledgements, args=(client, userdata), daemon=True)
            client.ack_check_thread.start()

def check_acknowledgements(client,userdata):
            global onAckLists, numRobots, amILeader
            time.sleep(5)  # Wait for 5 seconds before checking
            if len(onAckLists) == numRobots - 1: # -1 because the leader does not need to acknowledge itself
                client.publish(TOPIC_HI, f"{userdata} is your leader, thank you")
                onAckLists.clear()
            else:
                print(f"\n📡 Not all robots (should be {numRobots} Robots) acknowledged the leader. Re-election will be triggered by {userdata}...\n🤖 {userdata} > ", end="")
                # Re-election if not all robots acknowledged
                client.publish(TOPIC_ELECTION_REQUEST, f"{userdata} requests re-election due to missing acknowledgements")
                elect_captain(stub, userdata, client)

def start_message_listener(robot_id, stop_event, client):
    """
    Start the MQTT message listener for receiving commands from the broker.
    """
    client.user_data_set(robot_id)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT)
    client.loop_start()

    while not stop_event.is_set():
        # if error do not send online message!
        if not isError:
            client.publish(TOPIC_ONLINE, f"{robot_id}")
        time.sleep(1)

    client.loop_stop()
    client.disconnect()


def leader_election(stub, client, robot_id, election_id):
    """
    Perform leader election by broadcasting an election ID and determining
    the leader based on the highest election ID.
    
    Args:
        stub (robot_controller_pb2_grpc.RobotControllerStub): The gRPC stub instance
        client (mqtt.Client): The MQTT client instance.
        robot_id (str): The unique identifier for this robot/client.
    """
    global clients_messages, election_in_progress, amILeader

    # Broadcast the election ID to the MQTT topic
    clients_messages[robot_id] = election_id # Hopefully this will make sure that on_message this function will not be called twice!
    print(f"🤖 {robot_id} is broadcasting election ID {election_id}...")
    client.publish(TOPIC_ELECTION_ID, f"{robot_id}:{election_id}")

    # Allow time for all clients to respond
    print("📡 Waiting for responses from other clients...")
    time.sleep(5)

    # Determine the leader (robot with the highest election ID)
    if clients_messages:
        leader = max(clients_messages, key=clients_messages.get)
        if leader == robot_id:
            print(f"🏅 I am the leader with election ID {election_id}\n🤖 {robot_id} > ", end="")
            register_captain(stub, robot_id)
            amILeader = True
        else:
            amILeader = False
            onlineLists.clear()
            client.publish(TOPIC_ACK_LEADER, f"{robot_id}:{leader}")
            print(f"🏅 Leader elected: {leader} with election ID {clients_messages[leader]}\n🤖 {robot_id} > ", end="")
    else:
        print(f"⚠️ No responses received. No leader elected.\n🤖 {robot_id} > ", end="")
    
    # Clear messages for the next election round
    clients_messages.clear()
    election_in_progress = False  # Reset the flag


# gRPC Functions
def register_with_controller(stub, robot_id):
    robot_info = robot_controller_pb2.RobotInfo(id=robot_id)
    response = stub.RegisterRobot(robot_info)
    print(f"📩 Server response to {robot_id}: {response.message}")
    sys.stdout.flush()


def send_status_update(stub, robot_id, status):
    robot_status = robot_controller_pb2.RobotStatus(id=robot_id, status=status)
    response = stub.SendStatus(robot_status)
    print(f"📩 Server response to {robot_id}: {response.message}")
    sys.stdout.flush()


def unregister_with_controller(stub, robot_id):
    robot_info = robot_controller_pb2.RobotInfo(id=robot_id)
    response = stub.UnregisterRobot(robot_info)
    print(f"📩 Server response to {robot_id}: {response.message}")
    sys.stdout.flush()


def elect_captain(stub, robot_id, client):
    global election_in_progress
    if election_in_progress:
        print(f"⚠️ Election already in progress. Ignoring request.\n🤖 {robot_id} > ", end="")
        return
    if isError:
        print(f"⚠️ Robot is in error state. Cannot start election.\n🤖 {robot_id} > ", end="")
        return

    election_in_progress = True  # Set the flag
    captain_request = robot_controller_pb2.ElectionRequest()
    response = stub.ElectCaptain(captain_request)

    election_id = response.id
    print(f"> ElectionID: {election_id}")
    sys.stdout.flush()
    # leader_election(client, robot_id, election_id)
    # Start a new thread for leader election
    election_thread = threading.Thread(target=leader_election, args=(stub, client, robot_id, election_id), daemon=True)
    election_thread.start()

def register_captain(stub, robot_id):
    robot_info = robot_controller_pb2.RobotInfo(id=robot_id)
    response = stub.RegisterCaptain(robot_info)
    print(f"📩 Server response to {robot_id}: {response.message}")
    sys.stdout.flush()



# Context Manager for gRPC Channel
@contextmanager
def grpc_channel_context(target):
    channel = grpc.insecure_channel(target)
    try:
        yield channel
    finally:
        channel.close()


def print_help():
    print("\n🤖 Robot Control Help Menu 🤖")
    print("=" * 30)
    print("Commands:")
    print("  1  → Send health status")
    print("  2  → Start captain election")
    print("  3  → Quit program")
    print("  4  → Broadcast Hi")
    print("\n📢 To detach from Docker: Press 'Ctrl + P', then 'Ctrl + Q'\n")
    sys.stdout.flush()


# Main Application
def main(robot_id):
    with grpc_channel_context(f"{targetServer}:50051") as channel:
        global stub
        stub = robot_controller_pb2_grpc.RobotControllerStub(channel)
        client = mqtt.Client(robot_id)
        
        def signal_handler(sig, frame):
            print("\n")
            print(f"WARNING: {robot_id} is shutting down...")
            unregister_with_controller(stub, robot_id)
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        stop_event = threading.Event()

        # Start MQTT message listener in a separate thread
        listener_thread = threading.Thread(
            target=start_message_listener, args=(robot_id, stop_event, client), daemon=True
        )
        listener_thread.start()

        # Start user input handling in a separate thread
        input_thread = threading.Thread(target=handle_user_input, args=(robot_id, stub, stop_event, client), daemon=True)
        input_thread.start()

        # Keep main thread alive
        listener_thread.join()
        input_thread.join()


def handle_user_input(robot_id, stub, stop_event, client):
    register_with_controller(stub, robot_id)
    while True:
        user_input = get_user_input(robot_id)
        if handle_special_inputs(user_input):
            continue
        user_input_int = convert_input_to_int(user_input)
        if user_input_int is None:
            continue
        if process_user_command(user_input_int, robot_id, stub, stop_event, client):
            break


def get_user_input(robot_id):
    try:
        return input(f"🤖 {robot_id} > ").strip()
    except EOFError:
        print("\n⚠️ User detached. Waiting for reattachment...\n")
        sys.stdout.flush()
        time.sleep(1)
        return None


def handle_special_inputs(user_input):
    if user_input is None:
        return True
    if user_input == "help" or user_input == "h":
        print_help()
        return True
    if user_input == "":
        print()
        return True
    return False


def convert_input_to_int(user_input):
    try:
        return int(user_input)
    except ValueError:
        print(f"Input: {INVALID_INPUT_MESSAGE}\n")
        print_help()    
        return None


def process_user_command(user_input_int, robot_id, stub, stop_event, client):
    if user_input_int == 1:
        status = input("Enter the health status: ").strip()
        if status == "Error" or status == "error":
            global isError
            isError = True
        else:
            isError = False
        send_status_update(stub, robot_id, status)
    elif user_input_int == 2:
        elect_captain(stub, robot_id, client)
    elif user_input_int == 3:
        unregister_with_controller(stub, robot_id)
        print(f"🤖 {robot_id} is shutting down...")
        stop_event.set()
        sys.stdout.flush()
        return True
    elif user_input_int == 4:
        client.publish(TOPIC_HI, "hi")
    else:
        print(f"Int: {INVALID_INPUT_MESSAGE}")
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Robot Client")
    parser.add_argument("robot_id", help="Unique Robot Name")
    args = parser.parse_args()
    main(args.robot_id)