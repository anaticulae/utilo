pipeline {
    agent {
        docker {
            image '169.254.149.20:6001/arch_python_baw:0.10.4'
            args  '-v $WORKSPACE:/var/workdir'
        }
    }

    parameters {
        string(name: 'BRANCH', defaultValue: 'master')
        booleanParam(name: 'RELEASE', defaultValue: false)
    }

    stages{
        stage('sync'){
            steps{
                sh 'baw sync all'
                sh 'baw sh "pip install ."'
            }
        }
        stage('doctest'){
            steps{
                sh 'baw test docs -n1'
            }
        }
        stage('fast'){
            steps{
                sh 'baw test fast -n5'
            }
        }
        stage('long'){
            steps{
                sh 'baw test long -n8'
            }
        }
        stage('lint'){
            steps{
                sh 'baw lint'
            }
        }
        stage('nightly'){
            steps{
                sh 'baw test nightly -n16 --cov --junit_xml=report.xml'
                junit '**/report.xml'
            }
        }
        stage('others'){
            // TODO: REQUIRE INTEGRATION BRANCH BECAUSE MASTER ALWAYS WORKS
            when{ branch 'master' }
            parallel{
                stage('utilatest'){steps{build job: 'caelum/utilatest/master'}}
                stage('configo')  {steps{build job: 'caelum/configo/master'}}
                stage('iamraw')   {steps{build job: 'caelum/iamraw/master'}}
                stage('protocol') {steps{build job: 'caelum/protocol/master'}}
            }
        }
        stage('release'){
            when {
                expression { return params.RELEASE }
            }
            steps{
                sh 'baw install && baw release && baw publish'
                // TODO: GIT COMMIT?
            }
        }
    }
}
