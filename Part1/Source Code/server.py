# Name - Pashvi Prajapati (6855639) , Aman Yadav (6858054)
# Assign 2 , Part 1 - server file

#necessary libraries for implementation of sever program 
import socket
import threading
import zlib
import os
import base64
from cryptography.fernet import Fernet
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor, BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
#it samples all traces with always on strategy with the sampling with ratio 1
alwaysOnSampler = TraceIdRatioBased(1)
trace.set_tracer_provider(TracerProvider(sampler=alwaysOnSampler)) #configures the global tracer provider with always on sampling strategy
tracer = trace.get_tracer(__name__) #the tracer is been retrived with the specified name 
#the use of the jaeger exporter with the remote tracing for local agent 
jaegerExporter = JaegerExporter(
    agent_port=6831,
    agent_host_name="localhost",
)
#the following will setup the tracer provider and adds the span processor 
trace.get_tracer_provider().add_span_processor( #it exports the sample span for debugging to the console
    SimpleSpanProcessor(ConsoleSpanExporter())
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaegerExporter) #exports the batch span to the jaeger exporter 
)
ERROR_HANDLING = True
DECRYPTION = True 
#the following handle client function is responsible for handling the client connections 
def client_manage(clientSocket, address):
    with tracer.start_as_current_span("Server.py"): #the new span is started in teh distributed trace with the name server.py
        with clientSocket:
            try: #the part handles the file transfer 
                print(f"Connection has been established {address}") #prints the message that confirms the connection
                encrypted_filename = clientSocket.recv(1024) #the encoded filename has been successfully recieved 
                if DECRYPTION: #it then decodes the file using the base64 and the utf-8 while ignoring the errors 
                    file_name = base64.b64decode(encrypted_filename).decode('utf-8', 'ignore')
                    received_folder = "filesreceived" #the folder name has been specified for the recieved files 
                    os.makedirs(received_folder, exist_ok=True) #it creates the folder with the given name if none exists
                    received_filepath = os.path.join(received_folder, os.path.basename(file_name)) #it will have the complete filepath with the recieved folder and base filenames 
                    #the max number of retries is 3
                    for retry_count in range(3): 
                        try:
                            with open(received_filepath, "wb") as file: #opens the file in the binary write mode 
                                while True:
                                    data = clientSocket.recv(1024) #it loops through the data that has been recieved from the client 
                                    if not data: #if no more data is recieved
                                        break #the loop is broke
                                    file.write(data) #it indicates that the file transfer is successful
                            print(f"File have been received by {address} and saved to {received_filepath}.") #prints the messages that indicates the successful file transfer and been saved 
                            break #the loop has been exited since the trasnfer was successful
                        except Exception as e: #if any isssue occured during file handling, this will handle it
                            if ERROR_HANDLING: #it is it enabled  
                                print(f"Error handling encountered on client {address} - Retrying again: {e}") #prints a error message indicating a retry has been occuring
                                if retry_count < 2: #if the retry count is less than 2
                                    print("Retrying again.....")
                                    continue #it will continue to the next loop of retry
                                else: #if more than 2
                                    print("Maximum number of tries reached unable to receive the file :(") #prints a message indicating that the retry limit has been reached and unable to do more
                                    break #exit the loop
            except Exception as e: #it will catch any exception if occurred 
                print(f"Error handling client {address}: {e}") #prints the error message
#main function begins
def main():
    #sets the hosts and the port for the server
    host = '127.0.0.1'
    port = 8080
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    server.bind((host, port)) 
    server.listen(5) 
    print(f"Server is Listening {host}:{port}") #prints a message indicating that the server is listening to host and port 
# this will begin an infinte loop for client connections 
    while True:
        try:
            client, address = server.accept()
            client_handler = threading.Thread(target=client_manage, args=(client, address)) #a new thread for handling the client connection 
            client_handler.start() #it will start the thread 
        except Exception as e: #error handling if any occurs 
            print(f"Error encountered while accepting the connection from client side: {e}")
#main function
if __name__ == "__main__":
    main()
#end of program 