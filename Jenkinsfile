pipeline {
  agent any

  triggers {
    pollSCM '* * * * *'
    cron("H H(2-5) * * *")
  }

  options {
    disableConcurrentBuilds()
    checkoutToSubdirectory('inmanta-ui')
    skipDefaultCheckout()
  }

  stages {
    stage('clear workspace and checkout source code') {
      steps {
        deleteDir()
        dir('inmanta-ui') {
          checkout scm
        }
      }
    }
    stage("Cloning Inmanta core"){
      steps{
        dir('inmanta'){
            git branch: "master", url: 'https://github.com/inmanta/inmanta.git', poll: false, changelog: false
        }
      }
    }
    stage("Setup virtualenv"){
      steps{
        sh '''
          # Setup venv
          python3 -m venv ${WORKSPACE}/env
          ${WORKSPACE}/env/bin/python3 -m pip install -c ${WORKSPACE}/inmanta-ui/requirements.txt -U tox tox-venv setuptools pip
          source ${WORKSPACE}/env/bin/activate
          # build sdist of testing extension from source
          extra_dist=${WORKSPACE}/inmanta-ui/extra_dist
          cd inmanta/tests_common
          python3 copy_files_from_core.py
	      python3 setup.py sdist --dist-dir $extra_dist
          cd ..
          cd ..
        '''
      }
    }
    stage("Run tests"){
      steps{
        sh "${WORKSPACE}/env/bin/python -m tox -c inmanta-ui"
      }
    }
  }
  post {
    always{
        cobertura coberturaReportFile: 'inmanta-ui/coverage/cobertura.xml', failNoReports: false, failUnhealthy: false,

        failUnstable: false
    }
  }
}