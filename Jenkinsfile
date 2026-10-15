pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        DEPLOY_HOST          = 'eobserver'
        PROJECT_DIR          = '/home/eobkwaku/pdf-converter'
        DEPLOY_BRANCH        = 'trunk'
        DEPLOY_CREDENTIALS_ID = 'pdf-toolkit-deploy-key'
        REPO_URL             = 'https://github.com/edwardalx/pdf-toolkit'
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
                            bash -s -- "$PROJECT_DIR" "$DEPLOY_BRANCH" "$REPO_URL" <<'REMOTE'
                        set -eu
                        project_dir="$1"
                        deploy_branch="$2"
                        repo_url="$3"

                        # ------------------------------------------------------------
                        # 1. Ensure we have a valid git checkout at $project_dir
                        # ------------------------------------------------------------
                        if [ ! -d "$project_dir/.git" ]; then
                            echo "No git repository at $project_dir — bootstrapping."
                            mkdir -p "$(dirname "$project_dir")"

                            # If the directory exists and is non-empty, move it aside
                            if [ -d "$project_dir" ] && [ -n "$(ls -A "$project_dir" 2>/dev/null || true)" ]; then
                                backup="${project_dir}.bak.$(date +%s)"
                                echo "Directory not empty; moving aside to $backup"
                                mv "$project_dir" "$backup"
                            fi

                            git clone "$repo_url" "$project_dir"
                        fi

                        cd "$project_dir"

                        # ------------------------------------------------------------
                        # 2. Fetch and force the checkout onto origin/$deploy_branch
                        # ------------------------------------------------------------
                        echo "Fetching origin/$deploy_branch..."
                        git fetch --prune origin "$deploy_branch"

                        current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '')"
                        if [ "$current_branch" != "$deploy_branch" ]; then
                            echo "Switching from '$current_branch' to '$deploy_branch'..."
                            git checkout -B "$deploy_branch" "origin/$deploy_branch"
                        fi

                        # Deploy box → always converge to the exact remote commit
                        git reset --hard "origin/$deploy_branch"
                        git clean -fdx -e .env  # keep a local .env if you maintain one

                        echo "Deploying commit $(git rev-parse --short HEAD) on branch $(git rev-parse --abbrev-ref HEAD)"

                        # ------------------------------------------------------------
                        # 3. Build and start the stack
                        # ------------------------------------------------------------
                        echo "Building and starting Paperplane..."
                        docker compose up -d --build --remove-orphans

                        # ------------------------------------------------------------
                        # 4. Health check
                        # ------------------------------------------------------------
                        echo "Waiting for the API health check..."
                        for attempt in $(seq 1 30); do
                            if docker compose exec -T paperplane \
                                python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8080/api/health', timeout=3)" \
                                >/dev/null 2>&1; then
                                docker compose ps
                                echo "Deployment is healthy."
                                exit 0
                            fi
                            echo "  attempt $attempt/30: not ready yet..."
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