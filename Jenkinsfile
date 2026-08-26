pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Run OSPF Tests') {
            steps {
                sh '''
                    echo "Starting OSPF pyATS automation..."
                    python3 --version
                    /var/lib/jenkins/pyats_env/bin/pyats run job ospf_job.py
                '''
            }
        }
    }

    post {
        always {
            echo "OSPF automation pipeline completed."
        }

        success {
            echo "OSPF tests completed successfully."
        }

        failure {
            echo "OSPF tests failed."
        }
    }
}
