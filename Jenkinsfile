node {
  stage('Init') {
    checkout scm
  }
    
  stage('Build & Test') {
    try {
      sh 'docker-compose -f docker-compose.tests.yml -p hotmaps up --build --exit-code-from base_calculation_module'
    }
    finally {
      // stop services
      sh 'docker-compose -f docker-compose.tests.yml down' 
    }
  }
}
