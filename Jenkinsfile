// Jenkinsfile
def dockerImage

pipeline {
  agent any
  options { skipDefaultCheckout(true) }

  environment {
    DOCKER_HUB_REPO           = 'ritzmesh1/studyai'
    DOCKER_HUB_CREDENTIALS_ID = 'dockerHub-token'
    GITHUB_CREDENTIALS_ID     = 'github-token'
    KUBECONFIG_CREDENTIALS_ID = 'config'
    IMAGE_TAG                 = "v${BUILD_NUMBER}"

    // ArgoCD on EC2 via NodePort (you showed 30241)
    ARGO_SERVER    = '3.81.39.213:30241'
    ARGO_NAMESPACE = 'argocd'
  }

  stages {
    stage('Checkout GitHub') {
      steps {
        echo 'Checking out code from GitHub...'
        git url: 'https://github.com/RIT-MESH/Study-assistant.git',
            branch: 'main',
            credentialsId: "${GITHUB_CREDENTIALS_ID}"

        // safe repo (run with bash)
        sh '''bash -lc 'set -euo pipefail; git config --global --add safe.directory "$PWD"' '''
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
            dockerImage.push(env.IMAGE_TAG)
            dockerImage.push('latest')
          }
        }
      }
    }

    stage('Update deployment YAML with new tag') {
      steps {
        sh '''bash -lc '
          set -euo pipefail
          sed -E -i "s#(^\\s*image:\\s*).+#\\1${DOCKER_HUB_REPO}:${IMAGE_TAG}#" manifests/deployment.yaml
          echo "Updated manifests/deployment.yaml to ${DOCKER_HUB_REPO}:${IMAGE_TAG}"
          grep -nE "^\\s*image:" manifests/deployment.yaml || true
        ''''
      }
    }

    stage('Commit updated YAML back to GitHub') {
      steps {
        withCredentials([usernamePassword(credentialsId: "${GITHUB_CREDENTIALS_ID}",
                                          usernameVariable: 'GIT_USER',
                                          passwordVariable: 'GIT_PASS')]) {
          sh '''bash -lc '
            set -euo pipefail
            git config user.name  "RIT-MESH"
            git config user.email "ritzcloud12@gmail.com"
            git add manifests/deployment.yaml
            git commit -m "Update image tag to ${IMAGE_TAG}" || true
            git push "https://${GIT_USER}:${GIT_PASS}@github.com/RIT-MESH/Study-assistant.git" HEAD:main
          ''''
        }
      }
    }

    stage('Install kubectl & argocd cli (if missing)') {
      steps {
        sh '''bash -lc '
          set -euo pipefail
          command -v kubectl >/dev/null 2>&1 || {
            curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
            chmod +x kubectl && mv kubectl /usr/local/bin/kubectl
          }
          command -v argocd >/dev/null 2>&1 || {
            curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
            chmod +x /usr/local/bin/argocd
          }
        ''''
      }
    }

    stage('Argo CD: create-if-missing & sync') {
      steps {
        withCredentials([file(credentialsId: "${KUBECONFIG_CREDENTIALS_ID}", variable: 'KUBECONFIG')]) {
          sh '''bash -lc '
            set -euo pipefail

            echo "kubectl server -> $(kubectl config view --minify -o jsonpath="{.clusters[0].cluster.server}")"
            kubectl get ns

            PASS="$(kubectl -n ${ARGO_NAMESPACE} get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)"

            argocd login "${ARGO_SERVER}" --username admin --password "${PASS}" --insecure

            if ! argocd app get study >/dev/null 2>&1; then
              argocd app create study \
                --repo https://github.com/RIT-MESH/Study-assistant.git \
                --path manifests \
                --dest-server https://kubernetes.default.svc \
                --dest-namespace default \
                --revision main
            fi

            argocd app sync study
          ''''
        }
      }
    }
  }

  post {
    always  { sh 'docker image prune -f || true' }
    success { echo "Pushed: ${env.DOCKER_HUB_REPO}:${env.IMAGE_TAG} and :latest; updated manifest; ArgoCD synced." }
    cleanup { sh 'docker logout https://index.docker.io/v1/ || true' }
  }
}
