#!/usr/bin/env bash

set -euo pipefail

VERSION=$(./version.sh)

TMPDIR="/tmp/diagoriente-oplc/"
echo "Created temp dir $TMPDIR"

DOCKER_IMAGE_LOCAL=$TMPDIR/docker_images/$VERSION/all.tar

mkdir -p $TMPDIR/docker_images/$VERSION
echo "Saving docker images to $DOCKER_IMAGE_LOCAL"
docker save \
    $COMPOSE_PROJECT_NAME/frontend:$VERSION \
    $COMPOSE_PROJECT_NAME/api:$VERSION \
    $COMPOSE_PROJECT_NAME/streamlit:$VERSION \
    -o $DOCKER_IMAGE_LOCAL

RELEASE="${VERSION}-$(date -u --iso=seconds)"

echo "Sending docker images."
ssh ovh-vps-test "mkdir -p Diagoriente-Oplc/docker_images/$VERSION"
rsync -avHXS --numeric-ids --info=progress2 \
    $TMPDIR/docker_images/$VERSION/all.tar \
    ovh-vps-test:Diagoriente-Oplc/docker_images/$VERSION/

echo "Loading docker images on the server."
ssh ovh-vps-test "docker load -i Diagoriente-Oplc/docker_images/$VERSION/all.tar"

echo "Creating release ovh-vps-test:Diagoriente-Oplc/$RELEASE"
ssh ovh-vps-test "mkdir -p Diagoriente-Oplc/releases/$RELEASE"
rsync -av --info=progress2 .env-production ovh-vps-test:Diagoriente-Oplc/releases/$RELEASE/.env
rsync -av --info=progress2 \
    .version \
    docker/docker-compose.yaml \
    ovh-vps-test:Diagoriente-Oplc/releases/$RELEASE
