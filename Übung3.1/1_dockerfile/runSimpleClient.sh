#!/bin/bash

# Remove all .class files
rm -f */*.class

# Compile the Simple_Client.java
javac Simple_Client.java

# Check if the compilation was successful
if [ $? -eq 0 ]; then
    # Create the java_class directory if it doesn't exist
    mkdir -p java_class

    # Move the compiled .class files to the java_class directory
    mv *.class java_class/

    # Run the Simple_Client from the java_class directory
    java -cp java_class Simple_Client
else
    echo "Compilation failed."
fi