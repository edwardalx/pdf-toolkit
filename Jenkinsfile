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
                        # 2. Verify the checkout and fast-forward to origin/$deploy_branch
                        # ------------------------------------------------------------
                        current_branch="$(git rev-parse --abbrev-ref HEAD)"
                        if [ "$current_branch" != "$deploy_branch" ]; then
                            echo "Expected branch '$deploy_branch', found '$current_branch'." >&2
                            exit 1
                        fi

                        if [ -n "$(git status --porcelain)" ]; then
                            echo "Working tree is not clean; refusing to deploy." >&2
                            git status --short
                            exit 1
                        fi

                        # Existing checkouts may have a stale SSH origin. Use the
                        # configured URL, which allows public HTTPS repositories
                        # to fetch without server-side GitHub SSH credentials.
                        git remote set-url origin "$repo_url"

                        echo "Fetching origin/$deploy_branch..."
                        git fetch --prune origin "$deploy_branch"
                        git pull --ff-only origin "$deploy_branch"

                        echo "Deploying commit $(git rev-parse --short HEAD) on branch $(git rev-parse --abbrev-ref HEAD)"

                        # ------------------------------------------------------------
                        # 3. Build and start the stack
                        # ------------------------------------------------------------
                        echo "Building and starting Paperplane..."
                        docker compose -f compose.yaml -f compose.production.yaml up -d --build --remove-orphans

                        # ------------------------------------------------------------
                        # 4. Health check
                        # ------------------------------------------------------------
                        echo "Waiting for the API health check..."
                        for attempt in $(seq 1 30); do
                            if docker compose -f compose.yaml -f compose.production.yaml exec -T paperplane \
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
                        docker compose -f compose.yaml -f compose.production.yaml logs --tail=100 paperplane
                        exit 1
REMOTE
                    '''
                }
            }
        }

        stage('Sync nginx vhost') {
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
                            "set -eu
                            cd '$PROJECT_DIR'
                            echo 'Syncing nginx vhost...'
                            sudo -n cp deploy/nginx-paperplane.conf /etc/nginx/sites-enabled/pdf-gh
                            echo 'Testing nginx config...'
                            sudo -n nginx -t
                            echo 'Reloading nginx...'
                            sudo -n systemctl reload nginx
                            echo 'nginx vhost synced and reloaded.'"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Paperplane deployment and nginx sync completed successfully.'
        }
        failure {
            echo 'Paperplane deployment or nginx sync failed. Review the stage output.'
        }
    }
}
