#!/bin/bash
# The Travis CI build work flow.
# © 2018-2019 Cotes Chung
# MIT Licensed

USERNAME=cotes2020

POSTS_REPO=https://${GH_TOKEN}@github.com/${USERNAME}/blog-posts.git
META_REPO=https://${GH_TOKEN}@github.com/${USERNAME}/blog-meta.git
PV_REPO=https://${GH_TOKEN}@github.com/${USERNAME}/ga-pageviews.git

BLOG_REPO=https://${GH_TOKEN}@github.com/${USERNAME}/${USERNAME}.github.io.git
DEMO_REPO=https://${GH_TOKEN}@github.com/${USERNAME}/chirpy-demo.git

PROJ_LOCAL=$(pwd)   # equls to $TRAVIS_BUILD_DIR/$USERNAME/$CUR_PROJECT
POSTS_LOCAL=../blog-posts
META_LOCAL=../blog-meta
PV_CACHE=../ga-pageviews
DEPLOY_CACHE=../deploy


clear() {
  if [[ -d $1 ]]; then
    rm -rf $1
  fi
}


init() {
  # skip if build is triggered by pull request
  if [[ $TRAVIS_PULL_REQUEST == "true" ]]; then
    echo "this is PR, exiting"
    exit 0
  fi

  # enable error reporting to the console
  set -eu

  clear "_site"

  # Play trick
  echo "$CNAME" > CNAME

  CONFIG=_config.yml
  sed -i "s/\(^url:.*\)/url: 'https:\/\/${CNAME}'/g" $CONFIG
  sed -i "s/\(.*id:.*\)/  id: '${GA_ID}'/g" $CONFIG
  sed -i "s/\(.*shortname:.*\)/  shortname: '${DISQUS}'/g" $CONFIG
  sed -i "s/\(.*pv:.*\)/  pv: true/g" $CONFIG
  sed -i \
      "s/\(^google_site_verification:.*\)/google_site_verification: '${SITE_VERIFICATION}'/g" \
      $CONFIG

  # PV local cache
  wget $PV_PROXY_URL -O assets/data/pageviews.json -q

  # Proxy URL
  URL_FILE=assets/data/proxy.json
  tmp=$(mktemp)
  jq -c --arg PV_PROXY_URL $PV_PROXY_URL '.proxyUrl = $PV_PROXY_URL' $URL_FILE > $tmp && mv $tmp $URL_FILE

  # Git settings
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis-CI"

  git clone ${POSTS_REPO} ${POSTS_LOCAL}
  git clone ${META_REPO} ${META_LOCAL} --depth=1
  git clone $PV_REPO $PV_CACHE --depth=1

}


combine() {
  cd $PROJ_LOCAL

  TEMPLATE=(
    "_posts"
    "categories"
    "tags"
    "assets/img")

  for i in "${!TEMPLATE[@]}"
  do
    rm -rf ${TEMPLATE[${i}]}
  done

  cp -a ./* ${POSTS_LOCAL}
  echo "[$(date)] Combined posts."

  cp -a ${META_LOCAL}/* ${POSTS_LOCAL}
  echo "[$(date)] Combined meta-data."

  cp $PV_CACHE/* ${POSTS_LOCAL}/assets/data/
  echo "[$(date)] Combined with pv cache."
}


build() {
  build_cmd="JEKYLL_ENV=production bundle exec jekyll build"

  case $1 in
    $POSTS_LOCAL)
      combine
      ;;
    $PROJ_LOCAL)
      cp _docs/README.md ./
      ;;
    *)
      # do nothing
  esac

  cd $1
  echo "\$ cd $(pwd)"

  python _scripts/tools/init_all.py

  echo "\$ $build_cmd"
  eval $build_cmd

  echo "[$(date)] Build a site in $(pwd)"
}


wait_for_pages_build() {
  REPO_NAME=$1
  LATEST_COMMIT=$2
  CACHE=$REPO_NAME-status.json

  echo 'Waiting'

  while [[ true ]]
  do
    wait=5 # wait for gh pages build
    while [[ $wait -gt 0 ]]; do
      sleep 1
      echo -ne '.'
      ((wait--))
    done

    curl -H "Authorization: token $GH_TOKEN" \
      https://api.github.com/repos/${USERNAME}/${REPO_NAME}/pages/builds/latest \
      -o $CACHE -s

    pages_latest_commit=`jq -r '.commit' $CACHE`
    status=`jq -r '.status' $CACHE`

    if [[ $status == 'built' && $LATEST_COMMIT == $pages_latest_commit ]]; then
      echo "" # new line
      echo "[$(date)] GitHub Pages build for '$REPO_NAME' finished."
      break
    fi

    if [[ $status == 'errored' ]]; then
      echo ""
      echo "[$(date)] GitHub Pages build for '$REPO_NAME' error !"
      exit 1
    fi

  done
}


deploy() {
  # $1=build_proj, $2=deploy_repo
  build $1

  clear $DEPLOY_CACHE

  msg="Travis-CI automated deployment #${TRAVIS_BUILD_NUMBER}"

  git clone $2 $DEPLOY_CACHE --depth=1

  if [[ $2 == $DEMO_REPO ]]; then
    msg+="."
  else # deploy the Blog
    msg+=" from the Framework."
  fi

  rm -rf $DEPLOY_CACHE/*
  cp -r _site/* $DEPLOY_CACHE

  cd $DEPLOY_CACHE

  opt=""
  count=`git log --pretty=oneline | wc -l`

  if [[ $count > 0 ]]; then
    git update-ref -d HEAD # Overried the last commit message.
    opt="-f"
  fi

  git add -A
  git commit -m "$msg" -q
  git push $2 master:master $opt

  repo=$(basename $2)
  latest_commit=`git log -1 --pretty=oneline | awk '{print $1}'`

  if [[ $2 == $DEMO_REPO ]]; then
    wait_for_pages_build ${repo%.*} $latest_commit
  fi
}


main() {
  init
  deploy $PROJ_LOCAL  $DEMO_REPO
  deploy $POSTS_LOCAL $BLOG_REPO
}


main
