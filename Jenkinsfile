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
        string(name: 'dockerTagName', defaultValue: 's2tbx:testJenkins_validation', description: 'Snap version to use to launch tests')
    }
    stages {
        stage('GUI Tests') {
            agent { label 'snap-test' }
            steps {
                script {
                    docker.image('snap-build-server.tilaa.cloud/xvfb:1.0').withRun() { c ->
                        docker.image("snap-build-server.tilaa.cloud/${params.dockerTagName}").inside("--group-add 1006 --link ${c.id} -e DISPLAY=${c.id}:0 -v /data/ssd/testData/snap-gui-tests/qftest:/data/Products/qftest -v /opt/qftest/license:/home/snap/qftest/license") {
                            echo "Launch GUI Tests with ${env.JOB_NAME} from ${env.GIT_BRANCH} using docker image snap-build-server.tilaa.cloud/${params.dockerTagName}"
                            // sh 'rm -rf /home/snap/.snap/ && mkdir -p /home/snap/.snap/'
                            sh "rm -rf /home/snap/snap/snap/modules/org-esa-snap-snap-worldwind.jar"
                            sh "export qftest_data_dir=/data/Products/qftest && export qftest_snap_install_dir=/home/snap/snap/ && qftest_snap_user_dir=/home/snap/.snap && /usr/local/bin/qftest -batch -runlog $WORKSPACE/qftest_logs -report $WORKSPACE/qftest_report -suitesfile $WORKSPACE/qftests.lst"
                        }
                    }
                }
            }
            post {
                always {
                    sh "ls -l $WORKSPACE"
                    sh "ls -l $WORKSPACE/qftest_report"
                    archiveArtifacts artifacts: "qftest_report/report.html", fingerprint: true
                    junit "qftest_report/report_junit.xml"
                }
            }
        }
    }
    /*post {
        failure {
            step (
                emailext(
                    subject: "[SNAP] JENKINS-NOTIFICATION: ${currentBuild.result ?: 'SUCCESS'} : Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                    body: """Build status : ${currentBuild.result ?: 'SUCCESS'}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':
Check console output at ${env.BUILD_URL}
${env.JOB_NAME} [${env.BUILD_NUMBER}]""",
                    attachLog: true,
                    compressLog: true,
                    recipientProviders: [[$class: 'CulpritsRecipientProvider'], [$class:'DevelopersRecipientProvider']]
                )
            )
        }
    }*/
}
