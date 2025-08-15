// Jenkinsfile
def dockerImage

pipeline {
  agent any
  options { skipDefaultCheckout(true) }   // we do our own checkout

  environment {
    DOCKER_HUB_REPO            = 'ritzmesh1/studyai'   // Docker Hub repo (lowercase)
    DOCKER_HUB_CREDENTIALS_ID  = 'dockerHub-token'     // Jenkins creds: username + access token
    // IMAGE_TAG will be set in "Prepare" stage as v<BUILD_NUMBER>
  }

  stages {
    stage('Prepare') {
      steps {
        script {
          env.IMAGE_TAG = "v${env.BUILD_NUMBER}"
          echo "IMAGE_TAG set to ${env.IMAGE_TAG}"
        }
      }
    }

    stage('Checkout Github') {
      steps {
        echo 'Checking out code from GitHub...'
        git url: 'https://github.com/RIT-MESH/Study-assistant.git',
            branch: 'main',
            credentialsId: 'github-token'  // Jenkins creds: GitHub username + PAT
      }
    }

    stage('Build Docker Image') {
      steps {
        script {
          echo "Building image ${env.DOCKER_HUB_REPO}:${env.IMAGE_TAG}"
          dockerImage = docker.build("${env.DOCKER_HUB_REPO}:${env.IMAGE_TAG}")
        }
      }
    }

    stage('Push Image to DockerHub') {
      steps {
        script {
          echo "Pushing ${env.DOCKER_HUB_REPO}:${env.IMAGE_TAG} to Docker Hub"
          // For Docker Hub, use 'https://index.docker.io/v1/' (or just '')
          docker.withRegistry('https://index.docker.io/v1/', env.DOCKER_HUB_CREDENTIALS_ID) {
            dockerImage.push(env.IMAGE_TAG)  // versioned tag e.g., v12
            dockerImage.push('latest')       // also update :latest
          }
        }
      }
    }

    // -----------------------------
    // The stages below are kept for later; uncomment when ready.
    // -----------------------------

    // stage('Update Deployment YAML with New Tag') {
    //   steps {
    //     script {
    //       sh """
    //         sed -i 's|image: dataguru97/studybuddy:.*|image: dataguru97/studybuddy:${IMAGE_TAG}|' manifests/deployment.yaml
    //       """
    //     }
    //   }
    // }

    // stage('Commit Updated YAML') {
    //   steps {
    //     script {
    //       withCredentials([usernamePassword(credentialsId: 'github-token',
    //                                         usernameVariable: 'GIT_USER',
    //                                         passwordVariable: 'GIT_PASS')]) {
    //         sh '''
    //           git config user.name "RIT-MESH"
    //           git config user.email "ci-bot@example.com"
    //           git add manifests/deployment.yaml
    //           git commit -m "Update image tag to ${IMAGE_TAG}" || echo "No changes to commit"
    //           git push https://${GIT_USER}:${GIT_PASS}@github.com/RIT-MESH/Study-assistant.git HEAD:main
    //         '''
    //       }
    //     }
    //   }
    // }

    // stage('Install Kubectl & ArgoCD CLI Setup') {
    //   steps {
    //     sh '''
    //       echo 'Installing kubectl & ArgoCD CLI...'
    //       curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    //       chmod +x kubectl
    //       mv kubectl /usr/local/bin/kubectl
    //       curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
    //       chmod +x /usr/local/bin/argocd
    //     '''
    //   }
    // }

    // stage('Apply Kubernetes & Sync App with ArgoCD') {
    //   steps {
    //     script {
    //       // Requires appropriate plugin/step for kubeconfig; keep commented until ready
    //       // kubeconfig(credentialsId: 'kubeconfig', serverUrl: 'https://192.168.49.2:8443') {
    //       //   sh '''
    //       //     argocd login 34.45.193.5:31704 --username admin --password $(kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d) --insecure
    //       //     argocd app sync study
    //       //   '''
    //       // }
    //     }
    //   }
    // }
  }

  post {
    always {
      sh 'docker image prune -f || true'
    }
    success {
      echo "Pushed: ${env.DOCKER_HUB_REPO}:${env.IMAGE_TAG} and :latest"
    }
    cleanup {
      sh 'docker logout https://index.docker.io/v1/ || true'
    }
  }
}
