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

def register_with_controller(stub, robot_id):
    robot_info = robot_controller_pb2.RobotInfo(id=robot_id)
    response = stub.RegisterRobot(robot_info)
    print(f"🤖 {robot_id}: {response.message}")

def send_status_update(stub, robot_id, status):
    robot_status = robot_controller_pb2.RobotStatus(id=robot_id, status=status)
    response = stub.SendStatus(robot_status)
    print(f"🤖 {robot_id}: {response.message}")

def unregister_with_controller(stub, robot_id):
    robot_info = robot_controller_pb2.RobotInfo(id=robot_id)
    response = stub.UnregisterRobot(robot_info)
    print(f"🤖 {robot_id}: {response.message}")

def elect_captain(stub):
    captain_request = robot_controller_pb2.CaptainRequest()
    response = stub.ElectCaptain(captain_request)
    print(f"🏅 New captain elected: {response.new_captain}")

INVALID_INPUT_MESSAGE = "Invalid input. Please write 'help' for further information."

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
    print("\n📢 To detach from Docker: Press 'Ctrl + P', then 'Ctrl + Q'\n")

def main(robot_id):
    with grpc_channel_context(f'{targetServer}:50051') as channel:
        stub = robot_controller_pb2_grpc.RobotControllerStub(channel)
        register_with_controller(stub, robot_id)

        def signal_handler(sig, frame):
            print("\n")
            print(f'WARNING: {robot_id} is shutting down...')
            unregister_with_controller(stub, robot_id)
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        print("\n🔄 Waiting for user input... Attach to Docker to begin.")
        is_entered = False
        while True:
            try:
                user_input = input(f"🤖 {robot_id} > ").strip()
                if user_input == "help" or user_input == "h":
                    print_help()
                    continue
                if user_input == "" and is_entered:
                    print()
                    continue
                user_input_int = int(user_input)
            except ValueError:
                if not is_entered:
                    print_help()
                    is_entered = True
                else:
                    print(f"Input: {INVALID_INPUT_MESSAGE}")
                continue
            except EOFError:
                print("\n⚠️ User detached. Waiting for reattachment...\n")
                time.sleep(1)
                continue  # Keeps waiting for a new attachment

            if user_input_int == 1:
                status = input("Enter the health status: ").strip()
                send_status_update(stub, robot_id, status)
            elif user_input_int == 2:
                elect_captain(stub)
            elif user_input_int == 3:
                break
            else:
                print(f"Int: {INVALID_INPUT_MESSAGE}")

        unregister_with_controller(stub, robot_id)
        print('Robot Gracefully ending the process...')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Robot Client")
    parser.add_argument("robot_id", help="Unique Robot Name")
    args = parser.parse_args()
    main(args.robot_id)
