#!/usr/bin/env groovy

/**
 * Copyright (C) 2019 CS-SI
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the Free
 * Software Foundation; either version 3 of the License, or (at your option)
 * any later version.
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, see http://www.gnu.org/licenses/
 */

pipeline {
    agent { label 'snap-test' }
    parameters {
        string(name: 'dockerTagName', defaultValue: 'snap:master', description: 'docker tag name to use')
        string(name: 'frequency', defaultValue: 'daily', description: 'frequency tag to use')
    }
    stages {
        stage('GUI Tests') {
            agent { 
                docker {
                    image "snap-build-server.tilaa.cloud/${params.dockerTagName}"
                    label 'snap-execution' 
                    args "--group-add 1006 -v /data/ssd/testData/snap-gui-tests/qftest:/data/Products/qftest -v /opt/qftest/license:/home/snap/qftest/license"
                }
            }
            steps {
                echo "Prepare Tests"
                // init useful variables
                sh "export test_dir=$WORKSPACE/gui-tests-resources && export build_dir=${test_dir}/testBuild && script_dir=${test_dir}/script"
                // make build directory
                sh "mkdir ${build_dir}"
                // generate list of json file to execute
                sh "python3 ${script_dir}/filterjsontest.py ${test_dir}/tests/ > ${build_dir}/list"
                // build tests
                sh "python3 ${script_dir}/buildtests.py --rootdir $WORKSPACE --testdir ${test_dir} -f ${params.frequency} ${build_dir}/list"
                echo "Launch GUI Tests with ${env.JOB_NAME} from ${env.GIT_BRANCH} using docker image snap-build-server.tilaa.cloud/${params.dockerTagName}"
                // We use xvfb-run to emulate DISPLAY inside snap docker
                sh "export qftest_data_dir=/data/Products/qftest && export qftest_snap_install_dir=/home/snap/snap/ && export qftest_snap_user_dir=/home/snap/.snap && xvfb-run /usr/local/bin/qftest -batch -runlog $WORKSPACE/qftest_logs -report $WORKSPACE/qftest_report -suitesfile ${build_dir}/qftests.lst"
                // clean tests build
                sh "python3 ${script_dir}/posttests.py --rootdir $WORKSPACE --testdir ${test_dir}"
            }
            post {
                always {
                    sh "ls -l $WORKSPACE"
                    //sh "tar zcvf qftest_report.tgz qftest_report"
                    sh "ls -l $WORKSPACE/qftest_report"
                    archiveArtifacts artifacts: "qftest_report/**/*.*", fingerprint: true
                    junit "qftest_report/report_junit.xml"
                }
            }
        }
    }
    post {
        failure {
            step (
                emailext(
                    subject: "[SNAP] JENKINS-NOTIFICATION: ${currentBuild.result ?: 'SUCCESS'} : Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                    body: """Build status : ${currentBuild.result ?: 'SUCCESS'}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':
Check console output at ${env.BUILD_URL}
${env.JOB_NAME} [${env.BUILD_NUMBER}]""",
                    attachLog: true,
                    compressLog: true,
                    //to: "${SNAP_INTERNAL_MAIL_LIST}"
                    to: "omar.barrilero@c-s.fr, jean.seyral@c-s.fr"
                )
            )
        }
    }
}
