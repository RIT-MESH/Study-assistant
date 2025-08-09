

```markdown
# GitOps Pipeline Setup Guide for Infrastructure Roles

This guide outlines setting up a GitOps pipeline using GitHub, Docker, Minikube, Jenkins, and ArgoCD on a Google Cloud VM. It’s tailored for transitioning to infrastructure-related roles, leveraging your skills in cloud (AWS/Azure), networking, and embedded systems. This setup demonstrates proficiency in CI/CD, Kubernetes, and Infrastructure as Code (IaC), which are in high demand in Japan’s tech sector (e.g., cloud engineers, DevOps roles).

---

## 1. Initial Setup

### **Push Code to GitHub**
- Push your project code to a GitHub repository (e.g., `https://github.com/<your-username>/gitops-demo`).
- **Skill Relevance**: Showcases version control proficiency, critical for infra roles.

### **Create a Dockerfile**
- In your project root, create a `Dockerfile` to containerize your application.
  ```dockerfile
  FROM python:3.9-slim
  WORKDIR /app
  COPY . .
  RUN pip install -r requirements.txt
  CMD ["python", "app.py"]
  ```
- **Skill Relevance**: Docker expertise is essential for cloud and DevOps roles.

### **Create Kubernetes Manifest Directory**
- Create a `manifests/` directory for Kubernetes YAML files (e.g., `deployment.yaml`, `service.yaml`).
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
          image: <your-dockerhub-username>/gitops-demo:latest
          ports:
          - containerPort: 80
  ```
- **Skill Relevance**: Kubernetes manifests demonstrate IaC skills.

### **Create a VM Instance on Google Cloud**
- Navigate to **GCP → Compute Engine → VM Instances → Create Instance**.
- Settings:
  - **Name**: `gitops-vm`
  - **Region**: `asia-northeast1` (Tokyo, for Japan-based roles)
  - **Machine Type**: `e2-standard-4` (4 vCPUs, 16 GB RAM)
  - **Boot Disk**: Ubuntu 24.04 LTS, 256 GB SSD
  - **Firewall**: Allow HTTP/HTTPS traffic
- Create the instance and note the **External IP**.
- **Skill Relevance**: Cloud VM management is a core infra skill.

### **Connect to the VM**
- Use GCP’s browser-based **SSH** to connect.
- **Skill Relevance**: Familiarity with cloud platforms (GCP, AWS, Azure) is key for infra roles.

---

## 2. Configure VM Instance

### **Clone Your GitHub Repository**
```bash
git clone https://github.com/<your-username>/gitops-demo.git
cd gitops-demo
ls  # Verify project contents
```

### **Install Docker**
- Follow the official Docker documentation for Ubuntu:
  ```bash
  sudo apt-get update
  sudo apt-get install -y ca-certificates curl
  sudo install -m 0755 -d /etc/apt/keyrings
  sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  sudo chmod a+r /etc/apt/keyrings/docker.asc
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io
  ```
- Test Docker:
  ```bash
  sudo docker run hello-world
  ```
- Enable non-root Docker access:
  ```bash
  sudo usermod -aG docker $USER
  newgrp docker
  ```
- Enable Docker on boot:
  ```bash
  sudo systemctl enable docker.service containerd.service
  ```
- Verify:
  ```bash
  docker ps  # No containers running
  docker ps -a  # Shows hello-world
  systemctl status docker  # Should show "active (running)"
  ```
- **Skill Relevance**: Docker setup and management are critical for containerized infra.

---

## 3. Configure Minikube

### **Install Minikube**
- Install Minikube for a local Kubernetes cluster:
  ```bash
  curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
  sudo install minikube-linux-amd64 /usr/local/bin/minikube
  ```
- Start Minikube:
  ```bash
  minikube start --driver=docker
  ```
- **Skill Relevance**: Kubernetes is a top skill for cloud infrastructure roles.

### **Install kubectl**
- Install via snap:
  ```bash
  sudo snap install kubectl --classic
  ```
- Verify:
  ```bash
  kubectl version --client
  ```
- Check Minikube status:
  ```bash
  minikube status  # All components should be running
  kubectl get nodes  # Shows Minikube node
  kubectl cluster-info  # Cluster details
  docker ps  # Minikube container running
  ```
- **Skill Relevance**: kubectl proficiency is essential for Kubernetes management.

---

## 4. Jenkins Setup

### **Run Jenkins in Docker**
- Create a Docker network for Minikube compatibility:
  ```bash
  docker network create minikube
  ```
- Run Jenkins:
  ```bash
  docker run -d --name jenkins \
    -p 8080:8080 -p 50000:50000 \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $(which docker):/usr/bin/docker \
    --network minikube \
    -u root \
    jenkins/jenkins:lts
  ```
- Verify:
  ```bash
  docker ps  # Jenkins container running
  docker logs jenkins  # Copy admin password
  ```

### **Access Jenkins Web UI**
- Open: `http://<VM_EXTERNAL_IP>:8080`
- If inaccessible, create a firewall rule:
  - **GCP → VPC Network → Firewall → Create Firewall Rule**
    - Name: `allow-jenkins`
    - Network: `default`
    - Direction: Ingress
    - Action: Allow
    - Targets: All instances
    - Source IP: `0.0.0.0/0`
    - Protocols/Ports: `tcp:8080,50000`
- Paste the admin password, install suggested plugins, and create an admin user.
- **Skill Relevance**: Jenkins setup showcases CI/CD expertise.

### **Install Plugins**
- In **Manage Jenkins → Plugins**, install:
  - Docker
  - Docker Pipeline
  - Kubernetes
- Restart Jenkins:
  ```bash
  docker restart jenkins
  ```

### **Install Python and Pip**
- Enter Jenkins container:
  ```bash
  docker exec -it jenkins bash
  apt update
  apt install -y python3 python3-pip python3-venv
  ln -s /usr/bin/python3 /usr/bin/python
  exit
  ```
- Restart Jenkins:
  ```bash
  docker restart jenkins
  ```
- **Skill Relevance**: Python automation is valuable for infra scripting.

---

## 5. GitHub Integration with Jenkins

### **Generate GitHub Personal Access Token**
- **GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)**
  - Permissions: `repo`, `admin:repo_hook`, `workflow`
  - Copy the token.

### **Add GitHub Credentials to Jenkins**
- **Manage Jenkins → Credentials → System → Global → Add Credentials**
  - Kind: Username with password
  - Username: Your GitHub username
  - Password: GitHub token
  - ID: `github-token`
  - Description: `GitHub Token`

### **Create Jenkins Pipeline**
- **Jenkins Dashboard → New Item**
  - Name: `gitops`
  - Type: Pipeline
  - Pipeline Section:
    - Definition: Pipeline script from SCM
    - SCM: Git
    - Repository URL: `https://github.com/<your-username>/gitops-demo.git`
    - Credentials: `github-token`
    - Branch: `main`

### **Create Jenkinsfile**
- In your project root:
  ```bash
  vi Jenkinsfile
  ```
- Add:
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
                  checkout scmGit(branches: [[name: '*/main']], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/<your-username>/gitops-demo.git']])
              }
          }
          stage('Build Docker Image') {
              steps {
                  echo 'Building Docker image...'
                  sh 'docker build -t <your-dockerhub-username>/gitops-demo:latest .'
              }
          }
          stage('Push to DockerHub') {
              steps {
                  echo 'Pushing to DockerHub...'
                  sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                  sh 'docker push <your-dockerhub-username>/gitops-demo:latest'
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
- Save: `Esc`, `:wq!`, `Enter`.
- **Skill Relevance**: Jenkins pipelines demonstrate automation and CI/CD skills.

### **Push Jenkinsfile to GitHub**
```bash
git config --global user.email "<your-email>"
git config --global user.name "<your-username>"
git add .
git commit -m "Add Jenkinsfile for GitOps pipeline"
git push origin main
```
- Use GitHub username and token when prompted.

### **Test Jenkins Pipeline**
- In Jenkins, go to `gitops` pipeline → **Build Now**.
- Check logs for success.
- **Skill Relevance**: Pipeline automation is a key DevOps skill.

---

## 6. Build and Push Docker Image to DockerHub

### **Configure Docker in Jenkins**
- **Manage Jenkins → Tools → Docker Installations**
  - Name: `Docker`
  - Check: Install automatically
  - Source: docker.com

### **Create DockerHub Repository**
- On [DockerHub](https://hub.docker.com), create a repository: `<your-dockerhub-username>/gitops-demo`.

### **Generate DockerHub Access Token**
- **DockerHub → Account Settings → Security → New Access Token**
  - Name: `gitops-access`
  - Permissions: Read/Write
  - Copy the token.

### **Add DockerHub Credentials to Jenkins**
- **Manage Jenkins → Credentials → System → Global → Add Credentials**
  - Kind: Username with password
  - Username: Your DockerHub username
  - Password: DockerHub token
  - ID: `gitops-dockerhub`
  - Description: `DockerHub Access Token`

### **Trigger Jenkins Pipeline**
- Push changes to GitHub and trigger the pipeline in Jenkins.
- Verify the image on DockerHub: `https://hub.docker.com/r/<your-dockerhub-username>/gitops-demo`.

---

## 7. Install and Configure ArgoCD - Part 1

### **Check Namespaces**
```bash
kubectl get namespace
```

### **Create ArgoCD Namespace**
```bash
kubectl create namespace argocd
```

### **Install ArgoCD**
```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### **Validate ArgoCD**
```bash
kubectl get all -n argocd
```
- Ensure all pods are **Running** (wait if **Pending** or **CrashLoopBackOff**).

### **Change ArgoCD Service to NodePort**
```bash
kubectl edit svc argocd-server -n argocd
```
- Change `type: ClusterIP` to `type: NodePort`.
- Save: `:wq!`.
- Verify:
  ```bash
  kubectl get svc -n argocd
  ```
- Note the NodePort (e.g., `31704`).

### **Access ArgoCD UI**
- In a new SSH terminal:
  ```bash
  kubectl port-forward --address 0.0.0.0 svc/argocd-server 31704:80 -n argocd
  ```
- Open: `http://<VM_EXTERNAL_IP>:31704`
- Get admin password:
  ```bash
  kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
  ```
- Login: Username `admin`, Password from above.
- **Skill Relevance**: ArgoCD expertise is valuable for GitOps and Kubernetes automation.

---

## 8. Install and Configure ArgoCD - Part 2

### **Locate Kubeconfig**
```bash
cd ~
ls -la .kube/
cat .kube/config
```
- Copy the `config` content to a local file (e.g., `kubeconfig`).

### **Convert File Paths to Base64**
- For each file in `.kube/config` (e.g., `ca.crt`, `client.crt`, `client.key`):
  ```bash
  cat /home/<username>/.minikube/ca.crt | base64 -w 0
  cat /home/<username>/.minikube/profiles/minikube/client.crt | base64 -w 0
  cat /home/<username>/.minikube/profiles/minikube/client.key | base64 -w 0
  ```
- Replace `certificate-authority-data`, `client-certificate-data`, and `client-key-data` in `kubeconfig` with these base64 strings.

### **Save Kubeconfig in Jenkins**
- **Manage Jenkins → Credentials → System → Global → Add Credentials**
  - Kind: Secret file
  - File: Upload `kubeconfig`
  - ID: `kubeconfig`
  - Description: `Kubernetes Config`

### **Configure Kubernetes in Jenkins Pipeline**
- Get cluster URL:
  ```bash
  kubectl cluster-info
  ```
- Update `Jenkinsfile` with `kubernetes deploy` step (see Section 5).

---

## 9. Install and Configure ArgoCD - Part 3

### **Install ArgoCD CLI in Jenkins**
- Already included in `Jenkinsfile` (see `Install Kubectl & ArgoCD CLI` stage).

### **Connect GitHub to ArgoCD**
- In ArgoCD UI: **Settings → Repositories → Connect Repo**
  - Type: Git
  - Name: `gitops-demo`
  - Project: `default`
  - Repo URL: `https://github.com/<your-username>/gitops-demo.git`
  - Username: Your GitHub username
  - Password: GitHub token

### **Create ArgoCD Application**
- **Applications → New App**
  - Name: `gitops-app`
  - Project: `default`
  - Sync Policy: Automatic
  - Check: Auto-sync, Self Heal
  - Repository URL: Select your repo
  - Revision: `main`
  - Path: `manifests`
  - Cluster URL: Default cluster
  - Namespace: `argocd`
- Verify status: **Synced** and **Healthy**.

### **Sync ArgoCD in Jenkins**
- Already included in `Jenkinsfile` (see `Apply Kubernetes & Sync with ArgoCD` stage).

### **Verify Deployment**
```bash
kubectl get deploy -n argocd
kubectl get pods -n argocd
```

### **Allow External Access**
```bash
minikube tunnel
```
- In another terminal:
  ```bash
  kubectl port-forward svc/gitops-app -n argocd --address 0.0.0.0 9090:80
  ```
- Access: `http://<VM_EXTERNAL_IP>:9090`

---

## 10. Setup Webhooks

### **Add GitHub Webhook**
- **GitHub → Repository → Settings → Webhooks → Add webhook**
  - Payload URL: `http://<VM_EXTERNAL_IP>:8080/github-webhook/`
  - Content Type: `application/json`
  - Events: Just the `push` event
  - Enable SSL: If using HTTPS
  - Click: **Add webhook**

### **Configure Jenkins Webhook**
- **Jenkins → Pipeline → Configure**
  - Check: **GitHub hook trigger for GITScm polling**
  - Save.

### **Test Webhook**
- Modify `Jenkinsfile` in VS Code (e.g., add an `echo` statement).
- Push to GitHub:
  ```bash
  git add .
  git commit -m "Test webhook"
  git push origin main
  ```
- Verify Jenkins pipeline auto-triggers.

---

## Final Outcome
- Your GitOps pipeline automates code checkout, Docker image building/pushing, Kubernetes deployment, and ArgoCD syncing.
- Showcase this project in your portfolio (e.g., on `ritmesh.com` or GitHub) to demonstrate skills in CI/CD, Kubernetes, and GitOps for infrastructure roles in Japan.

---

## Tips for Infrastructure Job Transition
- **Portfolio**: Host this pipeline demo on GitHub and link it in your resume. Create a README with screenshots of Jenkins/ArgoCD UI.
- **Certifications**: Your AWS, Azure, and CCNA certs are strong. Consider adding Kubernetes (CKA) or Terraform Advanced.
- **Japanese Market**: Highlight this project in interviews to show automation (Jenkins), containerization (Docker), and orchestration (Kubernetes) skills. Mention familiarity with Japanese workplace culture (e.g., from CNC role).
- **Networking**: Share this project on LinkedIn or X (#DevOpsJapan) to connect with recruiters in Tokyo/Osaka.

---

This guide leverages your existing skills and aligns with Japan’s demand for cloud and DevOps engineers. Let me know if you need help with specific sections or job application strategies!
```

---

### Key Modifications and Improvements
1. **Simplified Instructions**: Streamlined commands and explanations for clarity, reducing redundancy (e.g., combined Docker installation steps).
2. **Updated Tools**: Used Ubuntu 24.04 LTS and latest Docker/Minikube commands for 2025 compatibility.
3. **Skill Relevance**: Added notes on how each step aligns with infrastructure job skills (e.g., CI/CD, Kubernetes, IaC).
4. **Job Transition Tips**: Included advice on showcasing this project for Japanese infra roles, leveraging your CNC and embedded systems background.
5. **Jenkinsfile Enhancements**: Added `environment` block for DockerHub credentials and structured stages for clarity.
6. **Security Best Practices**: Emphasized secure credential handling (e.g., kubeconfig, tokens).
7. **Japanese Context**: Focused on skills like Kubernetes and cloud automation, which are in high demand in Japan’s tech sector.

### Notes for Your Use
- Replace `<your-username>`, `<your-dockerhub-username>`, and `<VM_EXTERNAL_IP>` with your actual values.
- Add your application code (e.g., a Python Flask app) to the repository for a complete demo.
- Document this setup in your portfolio with screenshots and a video walkthrough (e.g., on your YouTube channel) to impress recruiters.
- Practice explaining this pipeline in Japanese (e.g., using terms like インフラ自動化, コンテナ化, CI/CD) for interviews.

Let me know if you need further refinements or specific additions (e.g., a sample app, additional certs, or job application templates)!