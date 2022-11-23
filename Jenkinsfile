@Library('caelum@ad13ec1bd1aa2006c015e6c6a9f9b7019e70d966') _

pipeline {
    agent {
        docker {
            image '169.254.149.20:6001/arch_python_git_baw:v1.25.0'
        }
    }
    stages{
        stage('setup'){
            steps{script{baw.setup()}}
        }
        stage('test'){
            failFast true
            parallel{
                stage('doc'){
                    steps{
                        script{baw.doctest()}
                    }
                }
                stage('fast'){
                    steps{
                        script{baw.fast()}
                    }
                }
                stage('long'){
                    steps{
                        script{baw.longrun()}
                    }
                }
            }
        }
        stage('all'){
            steps{
                script{baw.all()}
            }
        }
        stage('quality'){
            failFast true
            parallel{
                stage('lint'){
                    steps{
                        script{baw.lint()}
                    }
                }
                stage('format'){
                    steps{
                        script{baw.format()}
                    }
                }
            }
        }
        // stage('others'){
        // TODO: REQUIRE INTEGRATION BRANCH BECAUSE MASTER ALWAYS WORKS
        // when{ branch 'master' }
        //parallel{
        //    stage('utilatest'){steps{build job: 'caelum/utilatest/master'}}
        //    stage('configo')  {steps{build job: 'caelum/configo/master'}}
        //    stage('iamraw')   {steps{build job: 'caelum/iamraw/master'}}
        //    stage('protocol') {steps{build job: 'caelum/protocol/master'}}
        //}
        // }
        stage('release'){
            steps{
                script{publish.release()}
            }
        }
    }
}
