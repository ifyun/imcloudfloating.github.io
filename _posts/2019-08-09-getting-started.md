---
title: Getting Started
date: 2019-08-09 20:55:00 +0800
categories: [Blogging, Tutorial]
tags: [usage]
---


## Basic Environment

First of all, follow the [Jekyll Docs](https://jekyllrb.com/docs/installation/)  to complete the basic environment (Ruby, RubyGem, Bundler and Jekyll)  installation.

In addition, the [python](https://www.python.org/downloads/) and [ruamel.yaml](https://pypi.org/project/ruamel.yaml/) are also required.

## Configuration

Customize the variables in file `_data/meta.yml` as needed.

## Atom Feed

The Atom feed url of your site will be:

```
<site_uri>/feed.xml
```

The `site_uri` was defined by variabel **uri** in `_data/meta.yml`.

## Install Jekyll Plugins

In the root direcoty of the project, run the following command:

```
bundle install
```

`bundle` will install all dependent Jekyll Plugins declared in `Gemfile` that stored in the root automatically.

##  Run Locally

You may want to preview the site before publishing. Run the script in the root directory:

```
bash run.sh
```

>**Note**: Because the *Recent Update* required the latest git-log date of posts, make sure the changes of `_posts` have been committed before running this command. 

Open the brower and visit [http://127.0.0.1:4000](http://127.0.0.1:4000) 

##  Deploying to GitHub Pages

For security reasons, GitHub Pages runs on `safe` mode, which means the third-party Jekyll plugins or custom scripts will not work, thus **we have to build locally rather than on GitHub Pages**.

There are two basic types of GitHub Pages sites, therefore you can choose one of them to finish the publishing.

###  User and Organization Pages sites

1) Build your site by:

```console
$ cd /path/to/chirpy/
$ bash build.sh
```

The build results will be stored in `_site` of the project's root directory.

2) Go to GitHub website and create a new repository named `<username>.github.io`.

3) Copy the build results mentioned in ***1)*** to the new repository.
```terminal
$ pwd
/path/to/chirpy
$ cp -r _site/* /path/to/<username>.github.io
```

Then, push to remote:
```console
$ cd /path/to/<username>.github.io
$ git add -A && git commit -m "Your commit message"
$ git push origin master
```

4) Go to GitHub website and enable Pages service for the new repository `<username>.github.io`.

5) Visit `https://<username>.github.io` and enjoy.

###  Project Pages sites

If you want to put the source code and build results within one repository, the **Project Pages sites** is for you.

> **NOTE**: Do not name your repository `<username>.github.io`.

1) Suppose you have renamed the blog repository to `myblog`. Build the site with base url `/myblog`:

```console
$ cd /path/to/myblog/
$ bash build.sh --baseurl /myblog
```



> **Tips**: Setting the variable `baseurl` in `_config.yml` can revoke the parameter option `--baseurl /myblog` above .

2) Create a new branch `gh-pages` and ensure that there are no files in the new branch. Place the site files in folder `_site` into the root directory of the new branch, then push the new branch to the remote `origin/gh-pages`.

3) Go to GitHub website and enable Pages servies for the branch `gh-pages`
of the project.

4) Now your site is published at `https://<username>.github.io/myblog/`

## See Also

* [Write a new post]({{ site.baseurl }}/posts/write-a-new-post/)
* [Text and Typography]({{ site.baseurl }}/posts/text-and-typography/)
* [Customize the Favicon]({{ site.baseurl }}/posts/customize-the-favicon/)
