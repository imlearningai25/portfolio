/* ═══════════════════════════════════════════════════════════════════
   Niraj Byanjankar Portfolio — Jenkins CI/CD Pipeline
   ───────────────────────────────────────────────────────────────────
   Stages:
     1. Checkout        → pull source from GitHub
     2. Lint & Validate → basic Python syntax check
     3. Build Image     → docker build
     4. Push Image      → push to Docker Hub
     5. Deploy to K8s   → kubectl apply all manifests
     6. Verify Rollout  → confirm pods are running
   ═══════════════════════════════════════════════════════════════════ */

pipeline {

    agent any

    /* ── Global environment variables ─────────────────────────────── */
    environment {
        // Docker Hub image name — change DOCKER_HUB_USER to your Docker Hub username
        DOCKER_HUB_USER  = 'nirajbjk'
        IMAGE_NAME       = "${DOCKER_HUB_USER}/portfolio-portfolio"
        IMAGE_TAG        = "${BUILD_NUMBER}"          // e.g. portfolio:42
        IMAGE_LATEST     = "${IMAGE_NAME}:latest"
        IMAGE_VERSIONED  = "${IMAGE_NAME}:${IMAGE_TAG}"

        // Kubernetes namespace (must match k8s/namespace.yaml)
        K8S_NAMESPACE    = 'portfolio'

        // Jenkins credential IDs (configure these in Jenkins → Manage Credentials)
        DOCKERHUB_CREDS  = 'dockerhub-credentials'   // username + password
        KUBECONFIG_CREDS = 'kubeconfig'               // secret file
        GMAIL_SECRET_ID  = 'gmail-app-password'       // secret text
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))   // keep last 10 builds
        timestamps()                                      // show timestamps in logs
        timeout(time: 20, unit: 'MINUTES')               // fail if build takes > 20 min
    }

    stages {

        /* ── Stage 1: Checkout ──────────────────────────────────────── */
        stage('Checkout') {
            steps {
                echo '📥 Checking out source code...'
                checkout scm
                sh 'echo "Branch: $(git rev-parse --abbrev-ref HEAD)"'
                sh 'echo "Commit: $(git rev-parse --short HEAD)"'
            }
        }

        /* ── Stage 2: Lint & Validate ───────────────────────────────── */
        stage('Lint & Validate') {
            steps {
                echo '🔍 Validating Python syntax...'
                sh '''
                    python3 -m py_compile app.py
                    echo "✅ app.py syntax OK"
                '''
                echo '🔍 Validating Kubernetes manifests...'
                //sh 'apt install python3.13-venv -y'
                //sh 'python3 -m venv venv'
                //sh '. venv/bin/activate'

                sh 'pip install PyYAML --break-system-packages'
                sh '''
                    for f in k8s/*.yaml; do
                        python3 -c "import yaml, sys; yaml.safe_load_all(open('$f'))" \
                            && echo "✅ $f is valid YAML" \
                            || { echo "❌ $f has invalid YAML"; exit 1; }
                    done
                '''

            }
        }

        /* ── Stage 3: Build Docker Image ────────────────────────────── */
        stage('Build Image') {
            steps {
                echo "🐳 Building Docker image: ${IMAGE_VERSIONED}"
                sh """
                    docker build \
                        --tag ${IMAGE_VERSIONED} \
                        --tag ${IMAGE_LATEST} \
                        --build-arg BUILD_DATE=\$(date -u +%Y-%m-%dT%H:%M:%SZ) \
                        --build-arg VCS_REF=\$(git rev-parse --short HEAD) \
                        .
                    docker images | grep ${IMAGE_NAME}
                """
            }
        }

        /* ── Stage 4: Push to Docker Hub ────────────────────────────── */
        stage('Push Image') {
            steps {
                echo '📤 Pushing image to Docker Hub...'
                withCredentials([usernamePassword(
                    credentialsId: "${DOCKERHUB_CREDS}",
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin
                        docker push ${IMAGE_VERSIONED}
                        docker push ${IMAGE_LATEST}
                        docker logout
                        echo "✅ Pushed ${IMAGE_VERSIONED} and ${IMAGE_LATEST}"
                    """
                }
            }
        }
        /* ── Stage 5: Deploy to Kubernetes ────────────────────────────── */
        stage('Deploy to Kubernetes') {
            steps {
                echo '🚀 Deploying to Kubernetes cluster...'
                withCredentials([
                    string(credentialsId: "${GMAIL_SECRET_ID}", variable: 'GMAIL_PASS'),
                    string(credentialsId: "SECRET_KEY_ID", variable: 'SECRET_KEY')
                ]) {
                    sh """
                        export KUBECONFIG=\$KUBECONFIG
                        kubectl config view

                        kubectl apply -f k8s/namespace.yaml
                        kubectl apply -f k8s/configmap.yaml

                        CLEAN_PASS=\$(echo "\$GMAIL_PASS" | tr -d ' ')
                        kubectl create secret generic portfolio-secret \
                            --from-literal="GMAIL_APP_PASSWORD=\${CLEAN_PASS}" \
                            --from-literal="SECRET_KEY=\$SECRET_KEY" \
                            --namespace=${K8S_NAMESPACE} \
                            --dry-run=client -o yaml | kubectl apply -f -

                        sed -i 's|IMAGE_PLACEHOLDER|${IMAGE_VERSIONED}|g' k8s/deployment.yaml
                        kubectl apply -f k8s/deployment.yaml
                        kubectl apply -f k8s/service.yaml
                        kubectl apply -f k8s/hpa.yaml
                        kubectl apply -f k8s/ingress.yaml

                        echo "✅ All manifests applied"
                    """
                }
            }
        }

        /* ── Stage 6: Verify Rollout ─────────────────────────────────── */
        stage('Verify Rollout') {
            steps {
                echo '✅ Verifying deployment rollout...'
                withCredentials([file(credentialsId: "${KUBECONFIG_CREDS}", variable: 'KUBECONFIG')]) {
                    sh """
                        kubectl rollout status deployment/portfolio-deployment \
                            --namespace=${K8S_NAMESPACE} \
                            --timeout=180s

                        echo "── Pod status ──────────────────────────────"
                        kubectl get pods --namespace=${K8S_NAMESPACE} -o wide

                        echo "── Service & External IP ───────────────────"
                        kubectl get svc --namespace=${K8S_NAMESPACE}

                        echo "── HPA status ──────────────────────────────"
                        kubectl get hpa --namespace=${K8S_NAMESPACE}
                    """
                }
            }
        }
    }

    /* ── Post-build actions ────────────────────────────────────────── */
    post {
        success {
            echo """
            ╔══════════════════════════════════════╗
            ║  ✅ DEPLOYMENT SUCCESSFUL             ║
            ║  Image : ${IMAGE_VERSIONED}
            ║  Build : #${BUILD_NUMBER}
            ╚══════════════════════════════════════╝
            """
        }
        failure {
            echo """
            ╔══════════════════════════════════════╗
            ║  ❌ DEPLOYMENT FAILED                 ║
            ║  Build : #${BUILD_NUMBER}
            ║  Check the logs above for details    ║
            ╚══════════════════════════════════════╝
            """
        }
        always {
            // Clean up local Docker images to save disk space
            sh "docker rmi ${IMAGE_VERSIONED} ${IMAGE_LATEST} || true"
            cleanWs()
        }
    }
}
