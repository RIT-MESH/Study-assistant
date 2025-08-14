# GitOps Pipeline Demo for Infrastructure Roles

This repository demonstrates a **GitOps pipeline** using **GitHub**, **Docker**, **Minikube**, **Jenkins**, and **ArgoCD** deployed on an AWS EC2 instance. The project showcases skills in **CI/CD**, **Kubernetes**, **containerization**, and **Infrastructure as Code (IaC)**, aligning with Japan's tech industry demand for roles like Cloud Engineer, DevOps Engineer, and Infrastructure Specialist. 

![Pipeline Overview](https://via.placeholder.com/600x200.png?text=GitOps+Pipeline+Diagram) <!-- Replace with actual diagram -->

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
git clone https://github.com/RIT-MESH/gitops-demo.git
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

#### Create Jenkins Pipeline
- **Jenkins Dashboard → New Item**
  - Name: `gitops`
  - Type: Pipeline
  - Pipeline:
    - Definition: Pipeline script from SCM
    - SCM: Git
    - Repository URL: `https://github.com/RIT-MESH/gitops-demo.git`
    - Credentials: `github-token`
    - Branch: `main`

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
                checkout scmGit(branches: [[name: '*/main']], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/RIT-MESH/gitops-demo.git']])
            }
        }
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh 'docker build -t ritmesh/gitops-demo:latest .'
            }
        }
        stage('Push to DockerHub') {
            steps {
                echo 'Pushing to DockerHub...'
                sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                sh 'docker push ritmesh/gitops-demo:latest'
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
                    argocd app sync gitops-app
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
  git config --global user.email "contact@ritmesh.com"
  git config --global user.name "RIT-MESH"
  git add .
  git commit -m "Add Jenkinsfile"
  git push origin main
  ```
- Test pipeline: **Build Now**.
- **Skill Highlight**: Automation with Jenkins pipelines.

---

### 6. Build and Push Docker Image

#### Configure Docker in Jenkins
- **Manage Jenkins → Tools → Docker Installations**
  - Name: `Docker`
  - Install automatically: Check
  - Source: docker.com

#### Create DockerHub Repository
- Create: `ritmesh/gitops-demo` on [DockerHub](https://hub.docker.com).

#### Generate DockerHub Token
- **DockerHub → Account Settings → Security → New Access Token**
  - Name: `gitops-access`
  - Permissions: Read/Write
  - Copy token.

#### Add DockerHub Credentials
- **Manage Jenkins → Credentials → System → Global → Add Credentials**
  - Kind: Username with password
  - Username: `ritmesh`
  - Password: DockerHub token
  - ID: `gitops-dockerhub`
  - Description: `DockerHub Access Token`

#### Trigger Pipeline
- Push changes and verify image: `https://hub.docker.com/r/ritmesh/gitops-demo`.

---

### 7. Install ArgoCD - Part 1

#### Create Namespace
```bash
kubectl create namespace argocd
kubectl get namespace
```

#### Install ArgoCD
```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl get all -n argocd
```

#### Change to NodePort
```bash
kubectl edit svc argocd-server -n argocd
```
- Change `type: ClusterIP` to `type: NodePort`.
- Verify:
  ```bash
  kubectl get svc -n argocd
  ```

#### Access ArgoCD UI
```bash
kubectl port-forward --address 0.0.0.0 svc/argocd-server 31704:80 -n argocd
```
- Open: `http://<PUBLIC_IP>:31704`
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
  - Username: `RIT-MESH`
  - Password: GitHub token

#### Create ArgoCD Application
- **Applications → New App**
  - Name: `gitops-app`
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

#### Allow External Access
```bash
minikube tunnel
```
```bash
kubectl port-forward svc/gitops-app -n argocd --address 0.0.0.0 9090:80
```
- Access: `http://<PUBLIC_IP>:9090`

---

### 10. Setup Webhooks

#### Add GitHub Webhook
- **GitHub → Repository → Settings → Webhooks → Add webhook**
  - Payload URL: `http://<PUBLIC_IP>:8080/github-webhook/`
  - Content Type: `application/json`
  - Events: `push`
  - Enable SSL: If using HTTPS
  - Click: **Add webhook**

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
