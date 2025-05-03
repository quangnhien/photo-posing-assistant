pipeline {
  agent any

  environment {
    COMPOSE_PROJECT_NAME = "myapp"
    PROD_POSEMODEL_ENV_FILE = credentials('PROD_POSEMODEL_ENV_FILE')
    PROD_BACKEND_ENV_FILE = credentials('PROD_BACKEND_ENV_FILE')

    SERVER_IP = '172.200.176.26'
    SSH_KEY_ID = 'MODEL_VM_SSH_KEY'
  }

  stages {
    stage('Checkout Code') {
      steps {
        checkout scm
      }
    }

    stage('Only Run on Model Changes') {
      when {
        changeset "**/model/**"
      }
      steps {
        withCredentials([
          sshUserPrivateKey(credentialsId: "${SSH_KEY_ID}", keyFileVariable: 'KEY'),
          file(credentialsId: 'PROD_POSEMODEL_ENV_FILE', variable: 'POSEMODEL_ENV')
        ]) {
          sh """
            scp -o StrictHostKeyChecking=no -i $KEY \$POSEMODEL_ENV azureuser@$SERVER_IP:/home/azureuser/photo-posing-assistant/model/pose_server/.env

            ssh -o StrictHostKeyChecking=no -i $KEY azureuser@$SERVER_IP '
              echo "✅ Connected to remote server"
              cd photo-posing-assistant
              git pull
              cd model/pose_server
              echo "Contents of .env:"
              cat .env
              cd ..
              docker compose down
              docker compose up -d --build
            '
          """
        }
      }
    }

    stage('Only Run on App Changes') {
      when {
        changeset "**/app/**"
      }
      steps {
        withCredentials([
          sshUserPrivateKey(credentialsId: "${SSH_KEY_ID}", keyFileVariable: 'KEY'),
          file(credentialsId: 'PROD_BACKEND_ENV_FILE', variable: 'BACKEND_ENV')
        ]) {
          sh """
            scp -o StrictHostKeyChecking=no -i $KEY \$BACKEND_ENV azureuser@$SERVER_IP:/home/azureuser/photo-posing-assistant/app/backend/.env

            ssh -o StrictHostKeyChecking=no -i $KEY azureuser@$SERVER_IP '
              echo "✅ Connected to remote server"
              cd photo-posing-assistant
              git pull
              cd app/backend
              chmod 600 .env
              cd ..
              docker compose down
              docker compose up -d --build
            '
          """
        }
      }
    }
  }
}
