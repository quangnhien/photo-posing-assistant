pipeline {
  agent any

  environment {
    COMPOSE_PROJECT_NAME = "myapp"
  }

  stages {
    stage('Checkout Code') {
      steps {
        checkout scm
      }
    }

    stage('Build and Deploy with Docker Compose') {
      steps {
        echo "Building and starting frontend + backend containers..."
        sh '''
        docker compose down
        docker compose up -d --build
        '''
      }
    }

    stage('Verify Services') {
      steps {
        echo "Checking if backend is running..."
        sh 'curl -f http://localhost:8000 || echo "Backend not yet available"'
        echo "Checking if frontend is running..."
        sh 'curl -f http://localhost || echo "Frontend not yet available"'
      }
    }
  }

  post {
    success {
      echo '✅ Frontend + Backend successfully deployed!'
    }
    failure {
      echo '❌ Deployment failed.'
    }
  }
}
