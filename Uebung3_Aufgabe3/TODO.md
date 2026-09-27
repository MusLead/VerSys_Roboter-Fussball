# TODO

- Kassel, 27.09.2026 READMENYA PERLU DITAMBAHKAN TERUTAMA TTG MQTT YANG DIGUNAKAN APA!!!!

- Can the server send gRPC messages to the client? and the client respond? If yes, we could also test how the client responds to the server's messages
- When the server is down, the robot should be shutdown immdiately


Problem

if the docker down every server is down and left the dummy_robot alone,.. and then on again. The problem is that the election is always running and the dummy_robot does not give any respond to the other,... why??? I really wonder. Because it is not connected to the MQTT Server. it was connected to the MQTT Server before but not right now. Correct?