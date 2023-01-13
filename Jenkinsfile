@Library('caelum@refs/tags/v0.12.0') _

pipeline{
    agent{
        docker{
            image '169.254.149.20:6001/arch_python_git_baw:v1.52.0'
        }
    }
    stages{
        stage('integrate'){
            steps{script{baw.integrate()}}
        }
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
        stage('pre-release'){
            steps{
                script{baw.pre()}
            }
        }
        stage('others'){
            // TODO: REQUIRE INTEGRATION BRANCH BECAUSE MASTER ALWAYS WORKS
            when{branch 'develop'}
            parallel{
                stage('configo'){steps{build job: 'caelum/protocol/integrate'}}
                stage('iamraw'){steps{build job: 'caelum/iamraw/integrate'}}
                stage('protocol'){steps{build job: 'caelum/protocol/integrate'}}
                stage('utilatest'){steps{build job: 'caelum/utilatest/integrate'}}
            }
        }
        stage('release'){
            steps{
                script{
                    publish.release()
                    baw.rebase()
                }
            }
        }
    }
}
