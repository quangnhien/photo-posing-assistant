pipeline {
  agent any

  environment {
    COMPOSE_PROJECT_NAME = "myapp"
    prod_backend_env = credentials('prod_backend_env')
    prod_posemodel_env = credentials('prod_posemodel_env')
    model_server = credentials('model_server')

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
        withCredentials([sshUserPrivateKey(credentialsId: "${SSH_KEY_ID}", keyFileVariable: 'KEY')]) {
          sh '''
            ssh -o StrictHostKeyChecking=no -i $KEY ubuntu@$SERVER_IP << 'ENDSSH'
              echo "✅ Connected to remote server"
              cd /photo-posing-assistant
              git pull
              cd model/pose_server
              echo "$prod_posemodel_env" > .env
              chmod 600 .env
              cd ..
              docker-compose down
              docker-compose up -d --build
            ENDSSH
          '''
        }
      }
    }

    stage('Only Run on App Changes') {
      when {
        changeset "**/app/**"
      }
      steps {
        withCredentials([sshUserPrivateKey(credentialsId: "${SSH_KEY_ID}", keyFileVariable: 'KEY')]) {
          sh '''
            ssh -o StrictHostKeyChecking=no -i $KEY ubuntu@$SERVER_IP << 'ENDSSH'
              echo "✅ Connected to remote server"
              cd /photo-posing-assistant
              git pull
              cd app/backend
              echo "$prod_backend_env" > .env
              chmod 600 .env
              cd ..
              docker-compose down
              docker-compose up -d --build
            ENDSSH
          '''
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
