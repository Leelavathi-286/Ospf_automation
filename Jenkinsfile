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
                    export PATH="/var/lib/jenkins/pyats_env/bin:$PATH"

                    echo "Starting OSPF pyATS automation..."
                    python3 --version
                    which pyats
                    pyats version
                    pyats run job ospf_job.py
                '''
            }
        }
    }

    post {
        always {
            echo "OSPF automation pipeline completed."
        }
    }
}
