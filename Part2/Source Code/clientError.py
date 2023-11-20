# Name - Pashvi Prajapati (6855639) , Aman Yadav (6858054)
# Assign 2 , Part 2 - client error file

#necessary libraries for implementation of sever program
import socket
import os
import base64
import time 
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor, BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

#the following creates the sampler with the probability of 40%
probabilitySampler = TraceIdRatioBased(0.4)
#it sets the global tracer provider with the sampler that has been created 
trace.set_tracer_provider(TracerProvider(sampler=probabilitySampler))
tracer = trace.get_tracer(__name__) #access the tracer with the name mentioned 
#Jaeger exporter is defined for the local testing 
jaegerExporter = JaegerExporter(
    agent_port=6831,
    agent_host_name="localhost",
)
ERROR_HANDLING = True
ENCRYPTION = True
#the following adds the simple span processor to the console span exporter for local testing phase
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)
# the following adds the batch span processor to the jaeger exporter for the remote testing
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaegerExporter)
)
# the following funtion takes the filename, server address and retries as parameters
#In the following function we have removed the try and catch method.
def file_transfer(file_name, server_add, max_attempt=3):
    with tracer.start_as_current_span("clientError.py"): #begins the new span as a tracer function with the name given
        for reattempt in range(max_attempt + 1): #this loops through the number of max retries 
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket: #it will create a tcp scoket for the client
                client_socket.connect(server_add) #this will connect to the server
                if ENCRYPTION: #it will check if the encryption is enabled  
                    encrypted_filename = base64.b64encode(file_name.encode()).decode() 
                    client_socket.send(encrypted_filename.encode()) 
                with open(file_name, "rb") as file:
                    for data in file: #it will iterate through the file data in chunks 
                        client_socket.sendall(data) #sends the file data to the server
                print(f"{file_name} has been received by the server") #prints the message indicating that the file transfer has been successfull
                return #returns to the function 
#main function begins
def main():
    host = ('127.0.0.1', 8080) #defining the server
    path = "randomfiles" #the files has been sent to this folder name
    for root, _, files in os.walk(path): #it will iterate through the files in the specified folder 
        for file in files:
            file_path = os.path.join(root, file) #the file path 
            file_transfer(file_path, host,3)  #it will call the send file function for each of the files
#main function
if __name__ == "__main__":
    main()
#end of program 