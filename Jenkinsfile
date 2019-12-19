// Run the integration tests. When the master branch is used, a dev build is published to the internal devpi repository.
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

  environment {
    PIP_INDEX_URL='https://artifacts.internal.inmanta.com/inmanta/dev'
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
    stage("Package") {
      steps {
        sh '''
          source "${WORKSPACE}/env/bin/activate"
          make -C inmanta-ui build
        '''
      }
    }
    stage("Publish") {
      when {
        expression { env.BRANCH_NAME == 'master' }
      }
      steps {
        withCredentials([usernamePassword(credentialsId: 'devpi-user', passwordVariable: 'DEVPI_PASS', usernameVariable: 'DEVPI_USER')]) {
          sh '''
            source "${WORKSPACE}/env/bin/activate"
            make -C inmanta-ui upload-python-package
          '''
        }
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
