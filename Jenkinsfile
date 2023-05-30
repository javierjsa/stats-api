pipeline {
    agent {
        node {
            label 'docker-statsapi'
            }
      }
    triggers {
        pollSCM '* * * * *'
    }
    stages {
        stage('Build') {
            steps {
                echo "Building.."
                sh '''
                echo $PWD
                ls -la
                pip install -r requirements.txt
                pip install -r ./test/requirements.txt
                '''
            }
        }
        stage('Test') {
            steps {
                echo "Testing.."
                sh '''
                export PYTHONPATH=$PYTHONPATH:{$PWD}
                echo $PYTHONPATH
                cd test
                python -m unittest discover -s .
                '''
            }
        }
        stage('Deliver') {
            steps {
                echo 'Deliver....'
                sh '''
                echo "doing delivery stuff.."
                '''
            }
        }
    }
}