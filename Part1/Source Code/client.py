# Name - Pashvi Prajapati (6855639) , Aman Yadav (6858054)
# Assign 2 , Part 1 - Client file

#necessary libraries for implementation 
import socket
import os
import base64
import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor, BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

#the following creates the sampler with the probability of 40% by using the TraceIdRatioBased 
probabilitySampler = TraceIdRatioBased(0.4)
trace.set_tracer_provider(TracerProvider(sampler=probabilitySampler))
tracer = trace.get_tracer(__name__) #access the tracer with the name mentioned 
#Jaeger exporter is defined for the local testing 
jaegerExporter = JaegerExporter(
    agent_port=6831,
    agent_host_name="localhost",
)

#the following adds the simple span processor to the console span exporter for local testing phase
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)
# the following adds the batch span processor to the jaeger exporter for the remote testing 
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaegerExporter)
)
ERROR_HANDLING = True
ENCRYPTION = True
# the following funtion takes the filename, server address, encryption handling, error handling and retries as parameters 
def file_transfer(file_name, server_add, max_retries=3):
    with tracer.start_as_current_span("Client.py"):  #begins the new span as a tracer function with the name given
        #this loops through the number of max retries 
        for reattempt in range(max_retries + 1):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
                    clientSocket.connect(server_add) #TCP socket is created for communication 
                    #to check if the encryption is enabled 
                    if ENCRYPTION:
                        encrypted_filename = base64.b64encode(file_name.encode()).decode()
                        clientSocket.send(encrypted_filename.encode()) 
                    with open(file_name, "rb") as file: 
                        for data in file:
                            clientSocket.sendall(data) #the data in the file has been sent to the server
                    print(f"{file_name} has been received by the server")
                    return  
            except Exception as e:
                if ERROR_HANDLING: #if the error handling is enabled
                    print(f"Error encounter while sending  {file_name}: {e}") #this will print the error message for the filename
                #checks if the current retry count is less than the max retries
                if reattempt < max_retries:
                    timedelay = 2 ** reattempt  #it calculates the delay using the exponential backoff strategy
                    print(f"Retrying again in {timedelay} seconds..")
                    time.sleep(timedelay)#it will pause the execution for the estimated delay second that has been calculated 
                else: #otherwise if the max number of retries reached without a succesful transmission 
                    print(f"Maximum number of attempt has been made and unable to send the {file_name}.")

def main():
    server_add = ('127.0.0.1', 8080)#defining server address is defined
    source_path = "randomfiles" #the files has been sent to this folder name 
    for root, _, files in os.walk(source_path): #it will iterate through the files in the specified folder 
        for f in files:
            file_dir = os.path.join(root, f)
            file_transfer(file_dir, server_add,3)
#main function 
if __name__ == "__main__":
       main()
#end of program 