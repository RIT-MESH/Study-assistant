// Jenkinsfile
def dockerImage

pipeline {
  agent any
  options { skipDefaultCheckout(true) }

  environment {
    // ---- customize ONLY the values/IDs to match your Jenkins ----
    DOCKER_HUB_REPO            = 'ritzmesh1/studyai'      // <dockerhub-user>/<repo> (lowercase)
    DOCKER_HUB_CREDENTIALS_ID  = 'dockerHub-token'        // Jenkins creds: Docker Hub username + access token
    GITHUB_CREDENTIALS_ID      = 'github-token'           // Jenkins creds: GitHub username + PAT
    IMAGE_TAG                  = "v${BUILD_NUMBER}"

    // ArgoCD / Kube
    KUBECONFIG_CREDENTIALS_ID  = 'config'                 // Jenkins Secret file (your kubeconfig)
    KUBE_APISERVER_URL         = 'https://192.168.49.2:8443' // Minikube API (keep if that’s your cluster)
    ARGO_SERVER                = '3.81.39.213:31704'    // <<< REPLACE with your EC2 public IP:31704
    ARGO_NAMESPACE             = 'argocd'
  }

  stages {
    stage('Checkout GitHub') {
      steps {
        echo 'Checking out code from GitHub...'
        git url: 'https://github.com/RIT-MESH/Study-assistant.git',
            branch: 'main',
            credentialsId: "${GITHUB_CREDENTIALS_ID}"
        // avoid "unsafe repo" warnings inside Jenkins container
        sh 'git config --global --add safe.directory "$PWD"'
      }
    }

    stage('Build Docker image') {
      steps {
        script {
          echo "Building image ${DOCKER_HUB_REPO}:${IMAGE_TAG}"
          dockerImage = docker.build("${DOCKER_HUB_REPO}:${IMAGE_TAG}")
        }
      }
    }

    stage('Push to Docker Hub') {
      steps {
        script {
          echo "Pushing ${DOCKER_HUB_REPO}:${IMAGE_TAG} and :latest"
          docker.withRegistry('https://index.docker.io/v1/', "${DOCKER_HUB_CREDENTIALS_ID}") {
            dockerImage.push("${IMAGE_TAG}")   // v<N>
            dockerImage.push('latest')         // move latest
          }
        }
      }
    }

    stage('Update deployment YAML with new tag') {
      steps {
        // Replace the FIRST 'image:' line under your container with the new repo:tag
        sh """
          set -eux
          sed -E -i 's#(^\\s*image:\\s*).+#\\1${DOCKER_HUB_REPO}:${IMAGE_TAG}#' manifests/deployment.yaml
          echo 'Updated manifests/deployment.yaml to ${DOCKER_HUB_REPO}:${IMAGE_TAG}'
          grep -nE '^\\s*image:' manifests/deployment.yaml || true
        """
      }
    }

    stage('Commit updated YAML back to GitHub') {
      steps {
        withCredentials([usernamePassword(credentialsId: "${GITHUB_CREDENTIALS_ID}",
                                          usernameVariable: 'GIT_USER',
                                          passwordVariable: 'GIT_PASS')]) {
          sh '''
            set -eux
            git config user.name  "RIT-MESH"
            git config user.email "ritzcloud12@gmail.com"
            git add manifests/deployment.yaml
            git commit -m "Update image tag to ${IMAGE_TAG}" || true
            git push https://${GIT_USER}:${GIT_PASS}@github.com/RIT-MESH/Study-assistant.git HEAD:main
          '''
        }
      }
    }

    stage('Install kubectl & argocd cli (if missing)') {
      steps {
        sh '''
          set -eux
          command -v kubectl >/dev/null 2>&1 || {
            curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
            chmod +x kubectl && mv kubectl /usr/local/bin/kubectl
          }
          command -v argocd >/dev/null 2>&1 || {
            curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
            chmod +x /usr/local/bin/argocd
          }
        '''
      }
    }

    stage('Argo CD: create-if-missing & sync') {
      steps {
        // requires the "Kubernetes CLI" plugin for withKubeConfig
        withKubeConfig(credentialsId: "${KUBECONFIG_CREDENTIALS_ID}", serverUrl: "${KUBE_APISERVER_URL}") {
          sh '''
            set -eux
            # sanity check cluster
            kubectl get ns

            # fetch Argo admin password from cluster
            PASS="$(kubectl -n ${ARGO_NAMESPACE} get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d)"

            # login to Argo
            argocd login ${ARGO_SERVER} --username admin --password "$PASS" --insecure

            # ensure app "study" exists; create if missing
            if ! argocd app get study >/dev/null 2>&1; then
              argocd app create study \
                --repo https://github.com/RIT-MESH/Study-assistant.git \
                --path manifests \
                --dest-server https://kubernetes.default.svc \
                --dest-namespace default \
                --revision main
            fi

            # sync it
            argocd app sync study
          '''
        }
      }
    }
  }

  post {
    always {
      sh 'docker image prune -f || true'
    }
    success {
      echo "Pushed: ${DOCKER_HUB_REPO}:${IMAGE_TAG} and :latest"
    }
    cleanup {
      sh 'docker logout https://index.docker.io/v1/ || true'
    }
  }
}
