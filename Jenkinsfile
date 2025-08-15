// Jenkinsfile
def dockerImage

pipeline {
  agent any
  options { skipDefaultCheckout(true) }   // we do our own checkout

  environment {
    // ---- set these to match Jenkins credentials and your setup ----
    DOCKER_HUB_REPO            = 'ritzmesh1/studyai'    // <dockerhub-user>/<repo> (lowercase)
    DOCKER_HUB_CREDENTIALS_ID  = 'dockerHub-token'      // Docker Hub (username + access token)
    GITHUB_CREDENTIALS_ID      = 'github-token'         // GitHub (username + PAT)
    KUBECONFIG_CREDENTIALS_ID  = 'config'               // Secret file containing kubeconfig
    IMAGE_TAG                  = "v${BUILD_NUMBER}"

    // Argo CD (NodePort on the EC2 host)
    ARGO_SERVER                = '3.81.39.213:31704'    // <-- set to YOUR_PUBLIC_IP:NODEPORT
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
        sh '''
          #!/usr/bin/env bash
          set -euo pipefail
          git config --global --add safe.directory "$PWD"
        '''
      }
    }

    stage('Build Docker image') {
      steps {
        script {
          echo "Building image ${env.DOCKER_HUB_REPO}:${env.IMAGE_TAG}"
          dockerImage = docker.build("${env.DOCKER_HUB_REPO}:${env.IMAGE_TAG}")
        }
      }
    }

    stage('Push to Docker Hub') {
      steps {
        script {
          echo "Pushing ${env.DOCKER_HUB_REPO}:${env.IMAGE_TAG} and :latest"
          docker.withRegistry('https://index.docker.io/v1/', env.DOCKER_HUB_CREDENTIALS_ID) {
            dockerImage.push(env.IMAGE_TAG)   // versioned tag (e.g., v5)
            dockerImage.push('latest')        // also move :latest
          }
        }
      }
    }

    stage('Update deployment YAML with new tag') {
      steps {
        sh '''
          #!/usr/bin/env bash
          set -euo pipefail
          sed -E -i 's#(^\\s*image:\\s*).+#\\1'"${DOCKER_HUB_REPO}:${IMAGE_TAG}"'#' manifests/deployment.yaml
          echo "Updated manifests/deployment.yaml to ${DOCKER_HUB_REPO}:${IMAGE_TAG}"
          grep -nE '^\\s*image:' manifests/deployment.yaml || true
        '''
      }
    }

    stage('Commit updated YAML back to GitHub') {
      steps {
        withCredentials([usernamePassword(credentialsId: "${GITHUB_CREDENTIALS_ID}",
                                          usernameVariable: 'GIT_USER',
                                          passwordVariable: 'GIT_PASS')]) {
          sh '''
            #!/usr/bin/env bash
            set -euo pipefail
            git config user.name  "RIT-MESH"
            git config user.email "ritzcloud12@gmail.com"
            git add manifests/deployment.yaml
            git commit -m "Update image tag to ${IMAGE_TAG}" || true
            git push "https://${GIT_USER}:${GIT_PASS}@github.com/RIT-MESH/Study-assistant.git" HEAD:main
          '''
        }
      }
    }

    stage('Install kubectl & argocd cli (if missing)') {
      steps {
        sh '''
          #!/usr/bin/env bash
          set -euo pipefail
          if ! command -v kubectl >/dev/null 2>&1; then
            curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
            chmod +x kubectl && mv kubectl /usr/local/bin/kubectl
          fi
          if ! command -v argocd >/dev/null 2>&1; then
            curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
            chmod +x /usr/local/bin/argocd
          fi
        '''
      }
    }

    stage('Argo CD: create-if-missing & sync') {
      steps {
        // Use the kubeconfig Secret file (no extra plugin needed)
        withCredentials([file(credentialsId: "${KUBECONFIG_CREDENTIALS_ID}", variable: 'KUBECONFIG')]) {
          sh '''
            #!/usr/bin/env bash
            set -euo pipefail

            # sanity check cluster
            kubectl get ns

            # fetch Argo admin password from the cluster
            PASS="$(kubectl -n ${ARGO_NAMESPACE} get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d)"

            # login to ArgoCD via NodePort on the EC2 public IP
            argocd login "${ARGO_SERVER}" --username admin --password "${PASS}" --insecure

            # ensure the app "study" exists; create if missing
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
      echo "Pushed: ${env.DOCKER_HUB_REPO}:${env.IMAGE_TAG} and :latest, updated manifest, and synced ArgoCD."
    }
    cleanup {
      sh 'docker logout https://index.docker.io/v1/ || true'
    }
  }
}
