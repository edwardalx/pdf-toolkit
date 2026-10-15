pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        DEPLOY_HOST = 'eobserver'
        PROJECT_DIR = '/home/eobkwaku/pdf-converter'
        DEPLOY_BRANCH = 'trunk'
        DEPLOY_CREDENTIALS_ID = 'pdf-toolkit-deploy-key'
    }

    stages {
        stage('Deploy to server') {
            steps {
                withCredentials([sshUserPrivateKey(
                    credentialsId: "${DEPLOY_CREDENTIALS_ID}",
                    keyFileVariable: 'DEPLOY_KEY',
                    usernameVariable: 'SSH_USERNAME'
                )]) {
                    sh '''
                        set -eu
                        ssh -i "$DEPLOY_KEY" \
                            -o BatchMode=yes \
                            -o IdentitiesOnly=yes \
                            -o StrictHostKeyChecking=yes \
                            "$SSH_USERNAME@$DEPLOY_HOST" \
                            bash -s -- "$PROJECT_DIR" "$DEPLOY_BRANCH" <<'REMOTE'
                        set -eu
                        project_dir="$1"
                        deploy_branch="$2"

                        cd "$project_dir"
                        if [ -n "$(git status --porcelain)" ]; then
                            echo "Remote checkout has local changes; refusing to deploy over them."
                            exit 1
                        fi
                        if [ "$(git branch --show-current)" != "$deploy_branch" ]; then
                            echo "Remote checkout must be on branch $deploy_branch."
                            exit 1
                        fi

                        echo "Fetching $deploy_branch..."
                        git fetch origin "$deploy_branch"
                        git pull --ff-only origin "$deploy_branch"

                        echo "Building and starting Paperplane..."
                        docker compose up -d --build --remove-orphans

                        echo "Waiting for the API health check..."
                        for attempt in $(seq 1 30); do
                            if docker compose exec -T paperplane python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8080/api/health', timeout=3)" >/dev/null 2>&1; then
                                docker compose ps
                                echo "Deployment is healthy."
                                exit 0
                            fi
                            sleep 2
                        done

                        echo "Health check did not pass. Recent service logs:"
                        docker compose logs --tail=100 paperplane
                        exit 1
REMOTE
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Paperplane deployment completed successfully.'
        }
        failure {
            echo 'Paperplane deployment failed. Review the deploy stage output and remote Compose logs.'
        }
    }
}
