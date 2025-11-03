import socket

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect(("localhost",12345))
name = input("Введіть своє ім'я")
client_socket.send(name.encode())

message =client_socket.recv(1024). decode()
print(message)
client_socket.close()