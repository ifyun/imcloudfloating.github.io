---
title: Docker 实战—使用 Dockerfile 构建镜像
date: 2019-11-03 17:00 +0800
categories: [Docker]
tags: [Docker]

---

Dockerfile 指令详解请访问：[http://blog.cloudli.top/posts/Dockerfile-指令详解/](http://blog.cloudli.top/posts/Dockerfile-指令详解/)

## 使用 Alpine Linux 作为基础镜像

Alpine 是一个非常轻量的 Linux 镜像，他只有大约 5MB 的大小，基于它构建镜像，可以大大减少镜像的体积。

```shell
docker pull alpine
```

Alpine 使用 `apk` 命令来安装软件包，支持的软件包列表可以在官网查看：[https://pkgs.alpinelinux.org/packages](https://pkgs.alpinelinux.org/packages)

这里以安装 Nginx 为例，学习镜像的构建。另外 Nginx 本身有官方镜像，pull 即可。

## 构建 Nginx 镜像

### 编写 Dockerfile

```dockerfile
FROM alpine

RUN apk update \
    # 安装 nginx
    apk add --no-cache nginx \
    mkdir /run/nginx && \
    # 清除缓存
    rm -rf /tmp/* /var/cache/apk/*
    
# 添加容器启动命令，启动 nginx，以前台方式运行
CMD [ "nginx", "-g", "daemon off;" ]
```

这里有一个坑点，必须创建 `/run/nginx` 目录，不然会报错。

### 构建镜像

使用 `docker build` 命令构建：

```shell
docker build -t nginx-alpine .
```

在 Dockerfile 目录下执行以上命令即可构建镜像。`-t` 参数指定了镜像名称为 `nginx-alpine`，最后的 `.` 表示构建上下文（`.` 表示当前目录）.

**在使用 `COPY` 指令复制文件时，指令中的源路径是相对于构建上下文的**（如果指定上下文为 `/home`，那么相当于所有的源路径前面都加上了 `/home/`）。

如果你的 Dockerfile 文件名不是 “Dockerfile”，可以使用 `-f` 参数指定。

> **千万不要将 Dockerfile 放在根目录下构建，假如你将 Dockerfile 放在一个存放大量视频目录下，并且构建上下文为当前目录，那么镜像将会非常大（视频都被打包进去了）**。最佳做法是将 Dockerfile 和需要用到的文件放在一个单独的目录下。

## 运行容器

使用构建的镜像运行容器：

```shell
docker run --name my-nginx -p 80:80 -d nginx-apline
```

- `--name` 指定容器的名称，可以省略（后续只能通过容器 id 来操作）；
- `-p` 映射端口，宿主端口 -> 容器端口；
- `-d` 后台运行。

运行后访问 `http://localhost/`，会出现一个 nginx 的 404 页面，说明已经运行成功了，因为这里安装的 Nginx 并没有默认页面，`/etc/nginx/conf.d/default.conf` 中的内容：

```conf
# This is a default site configuration which will simply return 404, preventing
# chance access to any other virtualhost.

server {
        listen 80 default_server;
        listen [::]:80 default_server;

        # Everything is a 404
        location / {
                return 404;
        }
}
```

### 使用构建的 Nginx 镜像运行一个静态页面

在一个空目录下创建 Nginx 配置文件：

```conf
server {
        listen 80 default_server;
        listen [::]:80 default_server;

        root /var/www;
        
        location / {
                index index.html;
        }
}
```

编写一个静态页面：

```html
<!DOCTYPE html>
<html>
    <head>
        <title>Index</title>
    </head>
    <body>
        <h1>Hello, Docker!</h1>
    </body>
</html>
```

使用之前构建的镜像构建一个新的镜像：

```dockerfile
FROM nginx-alpine
# 拷贝配置文件，覆盖默认的
COPY default.conf /etc/nginx/conf.d/
# 拷贝静态页面
COPY index.html /var/www
```

构建镜像、运行容器：

```shell
docker build -t site .
```

```shell
docker run --name my-site -p 80:80 -d site
```

现在访问 `http://localhost/`，就可以看到 Hello, Docker!
