# GitOps Pipeline Demo for Infrastructure Roles

This repository demonstrates a **GitOps pipeline** using **GitHub**, **Docker**, **Minikube**, **Jenkins**, and **ArgoCD** deployed on an AWS EC2 instance. The project showcases skills in **CI/CD**, **Kubernetes**, **containerization**, and **Infrastructure as Code (IaC)**, aligning with Japan's tech industry demand for roles like Cloud Engineer, DevOps Engineer, and Infrastructure Specialist. 

<img width="1726" height="713" alt="image" src="https://github.com/user-attachments/assets/3b512dd9-92d5-43ed-8674-164fb955ca36" />
 <!-- Replace with actual diagram -->

## Project Overview

This pipeline automates:
- Code checkout from GitHub.
- Building and pushing Docker images to DockerHub.
- Deploying applications to a Kubernetes cluster via Minikube.
- Syncing deployments with ArgoCD for continuous delivery.

**Target Audience**: Recruiters, hiring managers, and tech enthusiasts looking for practical demonstrations of DevOps and infrastructure skills.

**Relevance**: Showcases proficiency in tools like Jenkins, Kubernetes, and ArgoCD, critical for Japan's growing cloud and automation sector (e.g., 63% IIoT adoption, 80,000+ cybersecurity job demand).

## Prerequisites

- **AWS Account**: For EC2 instance setup.
- **GitHub Account**: For repository hosting.
- **DockerHub Account**: For image storage.
- **Basic Linux Knowledge**: Familiarity with Ubuntu commands.
- **Tools**: Git, Docker, Minikube, kubectl, Jenkins, ArgoCD.
- **Sample App**: A simple Python Flask app (included as `app.py`).

## Setup Instructions

### 1. Initial Setup

#### Push Code to GitHub
- Clone this repository: `https://github.com/RIT-MESH/gitops-demo`.
- Add your application code (e.g., `app.py`, `requirements.txt`).
- Push to GitHub:
  ```bash
  git add .
  git commit -m "Initial commit"
  git push origin main
  ```
- **Skill Highlight**: Version control with Git.

#### Create a Dockerfile
- Create `Dockerfile` in the project root:
  ```dockerfile
  FROM python:3.9-slim
  WORKDIR /app
  COPY . .
  RUN pip install -r requirements.txt
  CMD ["python", "app.py"]
  ```
- **Skill Highlight**: Containerization with Docker.

#### Create Kubernetes Manifests
- Create a `manifests/` directory:
  ```bash
  mkdir manifests
  ```
- Example `manifests/deployment.yaml`:
  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: gitops-app
    namespace: argocd
  spec:
    replicas: 2
    selector:
      matchLabels:
        app: gitops-app
    template:
      metadata:
        labels:
          app: gitops-app
      spec:
        containers:
        - name: gitops-app
          image: ritmesh/gitops-demo:latest
          ports:
          - containerPort: 80
  ```
- Example `manifests/service.yaml`:
  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: gitops-app
    namespace: argocd
  spec:
    selector:
      app: gitops-app
    ports:
    - protocol: TCP
      port: 80
      targetPort: 80
    type: NodePort
  ```
- **Skill Highlight**: Kubernetes and IaC.

#### Create AWS EC2 Instance
- Navigate to **AWS Console → EC2 → Instances → Launch Instances**.
- Settings:
  - **Name**: `gitops-vm`
  - **AMI**: Ubuntu Server 24.04 LTS (HVM), SSD Volume Type
  - **Instance Type**: `t3.medium` (2 vCPUs, 4 GB RAM, scalable to 16 GB if needed)
  - **Key Pair**: Create or use an existing key pair for SSH access
  - **Network Settings**:
    - VPC: Default or create new
    - Security Group: Allow SSH (port 22), HTTP (port 80), HTTPS (port 443), and custom TCP ports (8080, 31704, 50000)
  - **Storage**: 256 GB gp3 SSD
- Launch the instance and note the **Public IPv4 address**.
- **Skill Highlight**: AWS infrastructure management.
<img width="1007" height="696" alt="スクリーンショット 2025-08-14 075923" src="https://github.com/user-attachments/assets/5ee23c04-881b-4e61-8b4d-eb589a56f4f7" />
#### Connect to EC2 Instance
- SSH using the key pair:

  ```bash
  ssh -i <your-key-pair>.pem ubuntu@<PUBLIC_IP>
  ```
- **Skill Highlight**: Cloud platform operations.

---

### 2. Configure EC2 Instance

#### Clone Repository
```bash
git clone https://github.com/RIT-MESH/Study-assistant.git
cd gitops-demo
ls
```

#### Install Docker
```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
docker run hello-world
sudo usermod -aG docker $USER
newgrp docker
sudo systemctl enable docker.service containerd.service
```
- Verify:
  ```bash
  docker ps
  docker ps -a
  systemctl status docker
  ```
- **Skill Highlight**: Docker setup and container management.
<img width="751" height="108" alt="スクリーンショット 2025-08-14 091513" src="https://github.com/user-attachments/assets/f18af785-7b41-4597-aa39-58e3b59158f7" />

<img width="666" height="129" alt="image" src="https://github.com/user-attachments/assets/5ca66540-b733-4fe1-a90f-5c62b3adefc0" />


---

### 3. Configure Minikube

#### Install Minikube
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube start --driver=docker
```

#### Install kubectl
```bash
sudo snap install kubectl --classic
kubectl version --client
```
- Verify Minikube:
  ```bash
  minikube status
  kubectl get nodes
  kubectl cluster-info
  docker ps
  ```
  <img width="663" height="221" alt="image" src="https://github.com/user-attachments/assets/0876c432-fceb-4aee-b78b-ec28bb9acd2c" />


- **Skill Highlight**: Kubernetes cluster management.

---

### 4. Jenkins Setup

#### Run Jenkins in Docker
```bash
docker network create minikube
docker run -d --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(which docker):/usr/bin/docker \
  --network minikube \
  -u root \
  jenkins/jenkins:lts
docker ps
docker logs jenkins
```
<img width="891" height="485" alt="image" src="https://github.com/user-attachments/assets/85fd16ca-5417-4a2b-842e-4a4c015a5c8f" />

#### Access Jenkins UI
- Open: `http://<PUBLIC_IP>:8080`
- If inaccessible, update the EC2 Security Group:
  - **AWS Console → EC2 → Security Groups → Edit Inbound Rules**
    - Add rules for:
      - TCP 8080 (Jenkins UI)
      - TCP 50000 (Jenkins agents)
      - TCP 31704 (ArgoCD)
    - Source: `0.0.0.0/0` (for demo; restrict in production)
- Use admin password from `docker logs jenkins`, install suggested plugins, and create an admin user.

<img width="1800" height="876" alt="image" src="https://github.com/user-attachments/assets/84bac65f-9a3a-4253-b061-256f2b875c55" />


#### Install Plugins
- In **Manage Jenkins → Plugins**, install:
  - Docker
  - Docker Pipeline
  - Kubernetes
- Restart:
  ```bash
  docker restart jenkins
  ```

#### Install Python and Pip
```bash
docker exec -it jenkins bash
apt update
apt install -y python3 python3-pip python3-venv
ln -s /usr/bin/python3 /usr/bin/python
exit
docker restart jenkins
```
- **Skill Highlight**: CI/CD pipeline setup with Jenkins.

![image](https://github.com/user-attachments/assets/44b60c6b-6abd-499e-bada-63e0bce1e20f)

![image](https://github.com/user-attachments/assets/118d9151-28fd-4940-b9d2-f431202ad67a)

![image](https://github.com/user-attachments/assets/392e992f-ccf2-4c28-a7e5-9bbb0dd7358a)

![image](https://github.com/user-attachments/assets/cc49fad2-e7fc-42cb-bca1-40fc6492811a)

![image](https://github.com/user-attachments/assets/bacf0595-45f5-47a2-959f-5b454f187ae9)

![image](https://github.com/user-attachments/assets/119db904-6da0-448a-ad70-79b6dd2311fb)






---

### 5. GitHub Integration

#### Generate GitHub Token
- **GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)**
  - Permissions: `repo`, `admin:repo_hook`, `workflow`
  - Copy token.

#### Add Credentials to Jenkins
- **Manage Jenkins → Credentials → System → Global → Add Credentials**
  - Kind: Username with password
  - Username: `RIT-MESH`
  - Password: GitHub token
  - ID: `github-token`
  - Description: `GitHub Token`
<img width="1766" height="451" alt="image" src="https://github.com/user-attachments/assets/c73c6163-3a60-4b3a-b568-6255f4d0daaa" />

#### Create Jenkins Pipeline
- **Jenkins Dashboard → New Item**
  - Name: `gitops`
  - Type: Pipeline
  - Pipeline:
    - Definition: Pipeline script from SCM
    - SCM: Git
    - Repository URL: `https://github.com/RIT-MESH/Study-assistant.git`
    - Credentials: `github-token`
    - Branch: `main`
<img width="1680" height="860" alt="image" src="https://github.com/user-attachments/assets/b53d8f2d-d4b4-4a70-8c6f-e0090677d6da" />

<img width="1516" height="845" alt="image" src="https://github.com/user-attachments/assets/9f648d2b-2c16-4825-aabb-a1fd4278070d" />

<img width="1471" height="813" alt="image" src="https://github.com/user-attachments/assets/8de75fbd-fec6-48ad-9ee2-af79a2e828ce" />

<img width="1658" height="816" alt="image" src="https://github.com/user-attachments/assets/f9cbddad-0139-4574-9a6d-e2fbc0d9d07d" />


#### Create Jenkinsfile
```bash
vi Jenkinsfile
```
```groovy
pipeline {
    agent any
    environment {
        DOCKERHUB_CREDENTIALS = credentials('gitops-dockerhub')
    }
    stages {
        stage('Checkout GitHub') {
            steps {
                echo 'Checking out code...'
                checkout scmGit(branches: [[name: '*/main']], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/RIT-MESH/Study-assistant.git']])
            }
        }
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh 'docker build -t ritmesh/stydyai:latest .'
            }
        }
        stage('Push to DockerHub') {
            steps {
                echo 'Pushing to DockerHub...'
                sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                sh 'docker push ritmesh/studyai:latest'
            }
        }
        stage('Install Kubectl & ArgoCD CLI') {
            steps {
                echo 'Installing Kubectl and ArgoCD CLI...'
                sh '''
                curl -LO https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl
                chmod +x kubectl
                mv kubectl /usr/local/bin/
                curl -sSL -o argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
                chmod +x argocd
                mv argocd /usr/local/bin/
                '''
            }
        }
        stage('Apply Kubernetes & Sync with ArgoCD') {
            steps {
                echo 'Applying Kubernetes manifests...'
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    sh '''
                    export KUBECONFIG=$KUBECONFIG
                    kubectl apply -f manifests/
                    argocd login <ARGOCD_SERVER_IP>:31704 --username admin --password $(kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d) --insecure
                    argocd app sync study
                    '''
                }
            }
        }
    }
}
```
- Save: `Esc`, `:wq!`.
- Push to GitHub:
  ```bash
  git config --global user.email "enteryour email here"
  git config --global user.name "your name"
  git add .
  git commit -m "Add Jenkinsfile"
  git push origin main
  ```
- Test pipeline: **Build Now**.
- **Skill Highlight**: Automation with Jenkins pipelines.

---
<img width="780" height="121" alt="image" src="https://github.com/user-attachments/assets/757815cb-0121-4184-943a-7d10a1ae0290" />

<img width="1327" height="817" alt="image" src="https://github.com/user-attachments/assets/3a8391fb-8486-4622-a2ec-ed3cd10b87bf" />

### 6. Build and Push Docker Image

#### Configure Docker in Jenkins
- **Manage Jenkins → Tools → Docker Installations**
  - Name: `Docker`
  - Install automatically: Check
  - Source: docker.com

<img width="884" height="881" alt="image" src="https://github.com/user-attachments/assets/4df9b6b9-2c3e-4e10-84a7-bad23939ca8c" />


#### Create DockerHub Repository
- Create: `ritmesh/studyai` on [DockerHub](https://hub.docker.com).

#### Generate DockerHub Token
- **DockerHub → Account Settings → Security → New Access Token**
  - Name: `llmops-token-1`
  - Permissions: Read/Write
  - Copy token.

#### Add DockerHub Credentials
- **Manage Jenkins → Credentials → System → Global → Add Credentials**
  - Kind: Username with password
  - Username: `ritmesh1`
  - Password: DockerHub token
  - ID: `dockerhub-token`
  - Description: `DockerHub Access Token`
<img width="723" height="731" alt="image" src="https://github.com/user-attachments/assets/3de74850-0781-4742-b02e-3ad8f6fdc309" />


#### Trigger Pipeline
- Push changes and verify image: `https://hub.docker.com/r/ritmesh/studyai`.

---
<img width="907" height="809" alt="image" src="https://github.com/user-attachments/assets/a312d794-9c8c-49ee-ae7d-83b0da1d4b34" />
<img width="1270" height="595" alt="image" src="https://github.com/user-attachments/assets/133298b3-af14-4aeb-99ea-17959d47b680" />


### 7. Install ArgoCD - Part 1

#### Create Namespace
```bash
kubectl create namespace argocd
kubectl get namespace
```
<img width="535" height="119" alt="image" src="https://github.com/user-attachments/assets/52cd4c77-2600-48c7-a5d1-d66534dceed9" />

#### Install ArgoCD
```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl get all -n argocd
```
<img width="989" height="526" alt="image" src="https://github.com/user-attachments/assets/256d62bb-b8bb-4c81-bada-f86d3ba8f284" />


#### Change to NodePort
```bash
kubectl edit svc argocd-server -n argocd
```
- Change `type: ClusterIP` to `type: NodePort`.
<img width="429" height="151" alt="image" src="https://github.com/user-attachments/assets/8fecd743-05fa-4903-994d-309b47b640e7" />

- Verify:
  ```bash
  kubectl get svc -n argocd
  ```
<img width="398" height="134" alt="image" src="https://github.com/user-attachments/assets/08d0ed78-5aca-47ff-8460-a7c9e73f27a5" />

#### Access ArgoCD UI
```bash
kubectl port-forward --address 0.0.0.0 svc/argocd-server 31704:80 -n argocd
```
- Open: `http://<PUBLIC_IP>:31704`
  <img width="1906" height="820" alt="image" src="https://github.com/user-attachments/assets/debb84fb-88de-4686-9217-ed51f03b8648" />

- Get admin password:
  ```bash
  kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
  ```
- Login: Username `admin`.
- **Skill Highlight**: ArgoCD for GitOps automation.

---

### 8. Install ArgoCD - Part 2

#### Locate Kubeconfig
```bash
cd ~
ls -la .kube/
cat .kube/config
```
- Copy `config` to a local file (e.g., `kubeconfig`).

#### Convert File Paths to Base64
```bash
cat /home/ubuntu/.minikube/ca.crt | base64 -w 0
cat /home/ubuntu/.minikube/profiles/minikube/client.crt | base64 -w 0
cat /home/ubuntu/.minikube/profiles/minikube/client.key | base64 -w 0
```
- Replace `certificate-authority-data`, `client-certificate-data`, and `client-key-data` in `kubeconfig`.

#### Save Kubeconfig in Jenkins
- **Manage Jenkins → Credentials → System → Global → Add Credentials**
  - Kind: Secret file
  - File: Upload `kubeconfig`
  - ID: `kubeconfig`
  - Description: `Kubernetes Config`

#### Configure Kubernetes in Jenkins
- Get cluster URL:
  ```bash
  kubectl cluster-info
  ```
- Update `Jenkinsfile` (see Section 5).

---

### 9. Install ArgoCD - Part 3

#### Connect GitHub to ArgoCD
- In ArgoCD UI: **Settings → Repositories → Connect Repo**
  - Type: Git
  - Name: `gitops-demo`
  - Project: `default`
  - Repo URL: `https://github.com/RIT-MESH/gitops-demo.git`
  - Username: `study`
  - Password: GitHub token
<img width="1532" height="271" alt="image" src="https://github.com/user-attachments/assets/a1b273a5-b32f-4835-9f0f-b2e60c7264cd" />

#### Create ArgoCD Application
- **Applications → New App**
  - Name: `study`
  - Project: `default`
  - Sync Policy: Automatic
  - Check: Auto-sync, Self Heal
  - Repository URL: Select repo
  - Revision: `main`
  - Path: `manifests`
  - Cluster URL: Default
  - Namespace: `argocd`
- Verify: **Synced** and **Healthy**.

#### Verify Deployment
```bash
kubectl get deploy -n argocd
kubectl get pods -n argocd
```
<img width="728" height="297" alt="image" src="https://github.com/user-attachments/assets/35e75dcd-75e5-4ff1-865a-ddc205d6a5f5" />



#### Allow External Access
```bash
minikube tunnel
```
<img width="449" height="172" alt="image" src="https://github.com/user-attachments/assets/858416e8-7a41-49a6-b029-857e337cb62a" />


```bash
kubectl port-forward svc/gitops-app -n argocd --address 0.0.0.0 9090:80
```
- Access: `http://<PUBLIC_IP>:9090`

---
<img width="1749" height="862" alt="image" src="https://github.com/user-attachments/assets/31a29ff8-c14c-4037-a25e-61dfddecf768" />


### 10. Setup Webhooks

#### Add GitHub Webhook
- **GitHub → Repository → Settings → Webhooks → Add webhook**
  - Payload URL: `http://<PUBLIC_IP>:8080/github-webhook/`
  - Content Type: `application/json`
  - Events: `push`
  - Enable SSL: If using HTTPS
  - Click: **Add webhook**
<img width="1003" height="785" alt="image" src="https://github.com/user-attachments/assets/c04f1aee-cf39-464e-9f99-2c6fdeb37112" />

#### Configure Jenkins Webhook
- **Jenkins → Pipeline → Configure**
  - Check: **GitHub hook trigger for GITScm polling**
  - Save.

#### Test Webhook
- Modify `Jenkinsfile` (e.g., add `echo`).
- Push:
  ```bash
  git add .
  git commit -m "Test webhook"
  git push origin main
  ```
- Verify auto-trigger in Jenkins.

---

## Final Outcome
This pipeline automates code checkout, Docker image building/pushing, Kubernetes deployment, and ArgoCD syncing. It’s a practical demonstration of DevOps skills for infrastructure roles.



---
