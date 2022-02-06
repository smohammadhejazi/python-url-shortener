# URL Shortener with Python
This project is a URL shortener written in python and deployed in minikube.  
The server code connects to MongoDB and stores the short URLs for later reverse requests.  
# How it works
First of all you need to install minikube and kubectl. minikube implements a local Kubernetes cluster on macOS, Linux, and Windows. Then after staring the cluster, you need to apply the resource files in order to start the servers to interact with them. All the files are in the kubectl-files directory.  
Also, the python server files are in the server-dockerfile directory which contains the dockerfile for server and the python code.  
# Run it
```sh
minikube start
kubectl apply -f <.yaml file>
```
You need to apply all the files in the kubectl-files directory, then for testing you can run a pod that has alpine and curl in order to test the server pods, or you can also do port forwarding so that you can test the server pods on your local machine.  
