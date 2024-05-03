## Kubernetes | Airflow
This project will cover some gaps on how to deploy airflow on kubernetes and how to interate with helm and kubectl as well. Make sure to install all dependencies before start the project:
- Install docker and docker-compose
- sudo snap install kubectl --classic
- sudo snap install helm --classic
- Install kind (step-by-step below)

### Concepts
- **Kubectl**:
  - **Purpose**: kubectl is the Kubernetes command-line tool used for interacting with Kubernetes clusters. It allows you to create, inspect, update, and delete Kubernetes resources such as pods, services, deployments, and more.
  - **Functionality**: With kubectl, you can perform a wide range of operations, including managing deployments, scaling applications, debugging, accessing logs, and executing commands within containers.
  - **Usage**: Administrators, developers, and operators use kubectl for day-to-day Kubernetes operations and management.
- **Helm**:
  - **Purpose**: Helm is a package manager for Kubernetes that simplifies the process of deploying, managing, and upgrading applications on Kubernetes clusters.
  - **Functionality**: Helm uses charts, which are packages of pre-configured Kubernetes resources, to define and manage complex applications. It provides commands to create, install, upgrade, and delete charts, as well as manage chart repositories.
  - **Usage**: DevOps engineers, software developers, and Kubernetes administrators use Helm to package, share, and deploy applications with ease, especially in scenarios involving complex application dependencies or configurations.
- **KIND** (Kubernetes IN Docker):
  - **Purpose**: KIND is a tool for running local Kubernetes clusters using Docker container "nodes". It's designed for development and testing purposes, allowing developers to quickly spin up Kubernetes clusters on their local machines.
  - **Functionality**: KIND creates lightweight Kubernetes clusters using Docker containers as nodes, making it easy to simulate multi-node Kubernetes environments on a single machine. It provides commands to create, start, stop, and delete Kubernetes clusters.
  - **Usage**: Developers and testers use KIND to develop, debug, and test Kubernetes applications locally before deploying them to production clusters. It's particularly useful for scenarios where developers need to iterate quickly and test their applications in an environment that closely resembles a production Kubernetes cluster.

### Install kind
**For AMD64 / x86_64**
```bash 
[ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.22.0/kind-linux-amd64
```

**For ARM64**
```bash
[ $(uname -m) = aarch64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.22.0/kind-linux-arm64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

### Manage Kind cluster
```bash
# Create the Cluster
kind create cluster --name airflow-cluster --config kind-cluster.yaml
# Check Clusters informations
kubectl cluster-info --context kind-airflow-cluster
# Check Kubernetes nodes
kubectl get nodes -o wide

# ------------------------------------------
# Delete a Cluster
kind delete cluster
# ------------------------------------------
```

### Deploy Airflow on Conteinerized Kubernetes (locally)
```bash
# Create a Namespace for airflow
kubectl create namespace airflow
# Check namespaces
kubectl get ns
# Add a repo of official airflow
helm repo add apache-airflow https://airflow.apache.org
# Update the repo airflow to latest version
helm repo update
#  Check your app and chart version of airflow 
helm search repo airflow
# Deploy airflow with debug tag as best practice
helm install airflow apache-airflow/airflow --namespace airflow --debug --timeout 10m0s
#Check informations of helm chart status as revision to rollback
helm ls -n <namespace>
```

### Check pods logs
```bash
# Get pods names
kubectl get pods -n <namespace>
# Check for logs in a specific pod
kubectl logs <pod_name> -n <namespace>
# If you have 2 or more container inside a pod, you need to specifi which one you want to get logs from
kubectl logs <pod_name> -n <namespace> -c scheduler
```

### Port forward
```bash
kubectl port-forward svc/airflow-webserver 8080:8080 -n airflow
```

### Export helm chart values, update and deploy
```bash
# Export the helm chart
helm show values apache-airflow/airflow > values.yaml
# Apply config map changes into airflow
kubectl apply -f variables.yaml
# Upgrade helm chart with changes
helm upgrade --install airflow apache-airflow/airflow -n <namespace> -f values.yaml --debug
# Check helm informations and see the difference on revision
helm ls -n <namespace>
# CAUTION: if you want to rollback
helm rollback <version>
```

### Execute bash inside a pod
```bash
# Get pods names
kubectl get pods -n <namespace>
# Exec bash inside webserver pod
kubectl exec --stdin --tty <pod_name> -n <namespace> -- /bin/bash
```

### Install external providers
Before starting, create a requirement.txt file qwith all needed providers. Also, create a Dockerfile to copy the requirements file into a container and run pip install -r inside the container.
```bash
# Build docker custom image with new providers
docker build -t airflow-custom:1.0.0 .
# Load Docker Image into a Kubernetes Cluster
kind load docker-image airflow-custom:1.0.0 --name airflow-cluster
```
After runing the code, change the values.yaml file to update the fields: ***defaultAirflowRepository*** and ***defaultAirflowTag*** to *airflow-custom* and *1.0.0*, respectively. Now, just upgrade helm chart as done before in this tutorial.

### Check Installed Providers
```bash
# Check the providers instaled on airflow
kubectl exec <airflow-webserver_name> -n airflow -- airflow info
```

### Configuring Logs with persistentVolumes
```bash
# Configure Persistent Volume
kubectl apply -f pv.yaml
kubectl get pv -n airflow
# Configure Persistent Volume Claim
kubectl apply -f pvc.yaml
kubectl get pvc -n airflow
```
After all, go to values.yaml file and enable ***logs*** and set ***existingClaim*** to *airflow-logs*. Do not forget to helm upgrade.

### Sync Git Repo
To this step, you should create a SSH key and paste or public key on your repository. On github, for example, go to Repo-> Settings-> Deploy Key-> Add Deploy Key.

Next, go to helm chart yaml file (values.yaml in this case), search for *gitSync* tag and enable it (change to true). Also keep your eyes on these tags:
- Repo: should contain the ssh url to clone
- branch: Usually is *main*, but could be another branch as well
- subPath: if your dag is inside a folder you must set this tag with the path, otherwise keep blank

In case of need a secret, you can create from your id_rsa using the command below:
```bash
kubectl create secret generic <secret_name> --from-file=gitSshKey=<path_to_id_rsa> -n <namespace>
```
After creating the secret, search for ***sshKeySecret*** on helm chart, uncomment the line and paste your secret_name there. Also, go to ***extraSecrets*** and include your base64 gitSshKey, any doubt reach values.yaml file and take a look.

Finnaly, upgrade your helm with the changes made with:
```bash
helm upgrade --install airflow apache-airflow/airflow -n airflow -f values.yaml --debug
```

### Get docker and KIND images hashes
Usually this stap is important on CI/CD because if any upcomming version on deploy has the same hash inside a database, most likely this code was paste from an older version and this is not allowed, so you can block the deploy on dev or prod
```bash
# From Docker
docker inspect --format='{{index .RepoDigests 0}}'
# From Kind
kind get nodes | xargs -n1 -I {} docker inspect --format='{{.RepoDigests}}' {}
```

### Troubleshooting
```bash
# Check logs on a pod
kubectl logs <pod_name> -c <container_name> -n <namespace>
# Review pod events
kubectl describe pod <pod_name> -n <namespace>
# Inspect container configurations
kubectl get pod <pod_name> -n <namespace> -o yaml
# Check resource contraints
kubectl describe pod <pod_name> -n <namespace> | grep -A 2 "Containers"
# Restart pod
kubectl delete pod <pod_name> -n <namespace>
```

### Links:
- https://github.com/marclamberti/webinar-airflow-chart
- https://kind.sigs.k8s.io/docs/user/quick-start
- https://www.youtube.com/watch?v=39k2Sz9jZ2c&ab_channel=Astronomer
- https://medium.com/go-city/deploying-apache-airflow-on-kubernetes-for-local-development-8e958675585d