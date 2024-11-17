#!/bin/bash

# Navigate to the directory containing TCPClient.java
cd /Users/aslam/Library/Mobile\ Documents/com~apple~CloudDocs/HS_Fulda/BSc_AInformatik/Verteilte\ System/group15/Übung3.1/1_dockerfile

# Compile the TCPClient.java
javac TCP_Client.java

# Check if the compilation was successful
if [ $? -eq 0 ]; then
    # Run the TCPClient
    java TCP_Client
else
    echo "Compilation failed."
fi