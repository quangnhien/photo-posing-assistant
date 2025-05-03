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
        withCredentials([sshUserPrivateKey(credentialsId: "${SSH_KEY_ID}", keyFileVariable: 'KEY'),file(credentialsId: 'PROD_POSEMODEL_ENV_FILE', variable: 'PROD_POSEMODEL_ENV_FILE')]) {
          sh """
            ssh -o StrictHostKeyChecking=no -i $KEY azureuser@$SERVER_IP << 'ENDSSH'
              echo "✅ Connected to remote server"
              cd photo-posing-assistant
              git pull
              cd model/pose_server

              echo "Copying .env from: $PROD_POSEMODEL_ENV_FILE"
              cp "$PROD_POSEMODEL_ENV_FILE" .env
              
              echo "Contents of .env:"
              cat .env
              chmod 600 .env

              cp $PROD_POSEMODEL_ENV_FILE .env
              echo "Contents of .env:"
              cat .env
              chmod 600 .env
              cd ..
              docker compose down
              docker compose up -d --build
            ENDSSH
          """
        }
      }
    }

    stage('Only Run on App Changes') {
      when {
        changeset "**/app/**"
      }
      steps {
        withCredentials([sshUserPrivateKey(credentialsId: "${SSH_KEY_ID}", keyFileVariable: 'KEY')]) {
          sh """
            ssh -o StrictHostKeyChecking=no -i $KEY azureuser@$SERVER_IP << 'ENDSSH'
              echo "✅ Connected to remote server"
              cd photo-posing-assistant
              git pull
              cd app/backend
              cp $PROD_BACKEND_ENV_FILE .env
              chmod 600 .env
              cd ..
              docker compose down
              docker compose up -d --build
            ENDSSH
          """
        }
      }
    }

    // Optional verification
    // stage('Verify Services') {
    //   steps {
    //     echo "Checking if backend is running..."
    //     sh 'curl -f http://localhost:8000 || echo "Backend not yet available"'
    //     echo "Checking if frontend is running..."
    //     sh 'curl -f http://localhost || echo "Frontend not yet available"'
    //   }
    // }
  }

  // post {
  //   success {
  //     echo '✅ Frontend + Backend successfully deployed!'
  //   }
  //   failure {
  //     echo '❌ Deployment failed.'
  //   }
  // }
}
