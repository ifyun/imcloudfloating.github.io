---
title: Dockerfile 指令详解
date: 2019-10-24 21:00 +0800
categories: [Docker]
tags: [Docker]

---

## FROM

`FROM` 命令指定基础镜像。在构建镜像时，基础镜像必须指定，因此在 `Dockerfile` 中 `FROM` 是必备指令且必须是第一条指令。

在 [Docker Hub](https://hub.docker.com/) 上有很多常用的高质量官方镜像，有一些是应用和服务类的镜像，如 [nginx](https://hub.docker.com/_/nginx)、[mysql](https://hub.docker.com/_/mysql
)、[redis](https://hub.docker.com/_/redis) 等；也有一些是用于运行各种语言应用的镜像，如 [openjdk](https://hub.docker.com/_/openjdk)、[python](https://hub.docker.com/_/python)、[node](https://hub.docker.com/_/node) 等。

如果找不到应用的官方镜像，可以基于操作系统镜像构建一个。Docker Hub 上提供了很多操作系统镜像。

```dockerfile
FROM ubuntu
...
```

## RUN

`RUN` 指令是用来执行命令行命令的。`RUN` 指令的格式有两种：

- shell 格式：`RUN <命令>`，就像直接在命令行中输入命令一样。

    ```dockerfile
    RUN java -jar app.jar
    ```
- exec 格式：`RUN ["可执行文件", "参数1", "参数2"]`。

    ```dockerfile
    RUN ["java", "-jar", "app.jar"]
    ```

在 `Dockerfile` 中，每一个指令都会在镜像上建立一层，所以对于多个命令行，不要写多个 `RUN` 指令。

对于多个命令，可以使用这样的写法：

```dockerfile
FROM ubuntu

RUN apt-get update \
    && apt-get install -y redis
```

对于多个命令，使用 `&&` 连接起来，只用一个 `RUN` 指令执行，这样就只会构建一层。

## COPY

`COPY` 指令用来将宿主的文件目录复制到镜像中。有两种格式：

- `COPY [--chown=<user>:<group>] <源路径>... <目标路径>`
    
    ```dockerfile
    COPY app.jar /usr/src/
    ```
    
- `COPY [--chown=<user>:<group>] ["源路径1", ... "目标路径"]`

    ```dockerfile
    COPY ["app.jar", "config.yml", "/usr/src"]
    ```

对于多个路径参数，最后一个为目标路径，其他都是源路径。`目标路径` 可以是绝对路径，也可以是相对于工作目录的路径（工作目录可以用 `WORKDIR` 来指定）。目标路径如果不存在，在复制文件前会先创建。

## CMD

`CMD` 是容器启动命令，它指定了容器启动后要执行的程序。与 `RUN` 指令相似有两种形式：

- shell 格式：`CMD <命令>`

    ```dockerfile
    CMD echo 'Hello, world!''
    ```
    
- exec 格式：`CMD ["可执行文件", "参数1", "参数2", ...]`

    ```dockerfile
    CMD [ "sh", "-c", "echo 'Hello, world!'" ]
    ```
    
还有一种参数列表格式：`CMD ["参数1", "参数2", ...]`。在指定了 `ENTRYPOINT` 指令后，可以用 `CMD` 指定参数。

在使用 `CMD` 时，程序必须以前台运行，Docker 不是虚拟机，容器没有后台服务的概率。如果使用 `CMD` 运行一个后台程序，那么容器在命令执行完就会退出。

```dockerfile
CMD java -jar app.jar &
```

以上命令让 app.jar 在后台运行，容器启动后就会立刻退出。Docker 容器与守护线程很相似，当所有前台程序退出后，容器就会退出。

`CMD` 指定的命令可以在运行时替换，跟在镜像名称后面的参数将替换镜像中的 `CMD`。

```shell
docker run app echo $HOME
```

以上命令运行容器时使用 `echo $HOME` 替换掉镜像中的启动命令。

## ENTRYPOINT

`ENTRYPOINT` 的格式与 `CMD` 一样有两种格式。

它和 `CMD` 一样都是指定容器启动的程序和参数，但稍有区别。当指定了 `ENTRYPOINT` 后，`CMD` 的内容将作为参数加到 `ENTRYPOINT` 后面。

也就是变成了：

```dockerfile
<ENTRYPOINT> "<CMD>"
```

`ENTRYPOINT` 可以让镜像像命令一样使用，当仅仅使用 `CMD` 时，`run` 命令中镜像名后面的参数会替换 `CMD` 的内容。使用 `ENTRYPOINT` 后，这些参数将附加到原来命令的后面。

```dockerfile
FROM alpine
ENTRYPOINT [ "ls" ]
```

使用以上 `Dockerfile` 构建的镜像运行容器：

```shell
docker run app -al
```

`-al` 参数将附加到 `ENTRYPOINT` 指定的命令后面，当容器启动时执行的是 `ls -al`。

## ENV

`ENV` 指令用来设置环境变量，格式有两种：

- `ENV <key> <value`
- `ENV <key1>=<value1> <key2>=<value2>`

环境变量在后面的其它指令中可以通过 `$key` 来使用：

```dockerfile
FROM ubuntu
ENV VERSION="8-jre"

RUN apt-get update \
    && apt-get install -y openjdk-$VERSION
...
```

## ARG

`ARG` 指令指定构建参数，与 `ENV` 效果一样，都是设置环境变量。不同的是，`ARG` 设置的构建参数，在容器运行时不存在。

格式：`ARG <key>[=<默认值>]`，可以指定默认值，也可以不指定。

```dockerfile
FROM alpine
ARG NAME="Hello, Docker!"

RUN echo $NAME
CMD echo $NAME
```

对于以上 `Dockerfile`，在构建时可以看到输出，但是在运行容器时没有输出。

`ARG` 设置的参数可以在构建命令中指定：`docker build --build-arg <key>=<value>`。

## VOLUME

`VOLUME` 指令用来定义匿名卷。

- `VOLUME <路径>`
- `VOLUME ["路径1", "路径2", ...]`

对于数据库类需要保持数据的应用，其文件应该保存于卷（volume）中，在 `Dockerfile` 中，可以事先将指定的目录挂载为匿名卷。

```dockerfile
VOLUME /data
```

这里 `/data` 目录在容器运行时自动挂载为匿名卷，任何写入 `/data` 中的数据都不会记录到容器的存储层。在运行时可以覆盖这个挂载设置：

```dockerfile
docker run -v dbdir:/data
```

以上命令将 `dbdir` 目录挂载到了 `/data`，替换了 `Dockerfile` 中的挂载配置。

## EXPOSE

`EXPOSE` 指令指定容器运行时暴露的端口。格式：`EXPOSE <端口1> [<端口2> ...]`。

```dockerfile
FROM ubuntu
EXPOSE 8080

RUN apt-get update \
    && apt-get install -y tomcat8
...
```

以上 `Dockerfile` 安装了 tomcat 应用，在运行容器时会暴露 8080 端口。

`EXPOSE` 只是指定了容器暴露的端口，并不会在宿主机进行端口映射。在使用 `docker run -P` 时，会自动随机映射 `EXPOSE` 指定的端口，也可以使用 `-p` 指定端口：`docker run -p <宿主端口>:<容器端口>`。

## WORKDIR

`WORKDIR` 指令指定工作目录，即指定当前目录，类似于 `cd` 命令，以后各层的当前目录都是 `WORKDIR` 指定的目录。如果目录不存在，会自动创建。格式：`WORKDIR <目录路径>`。

不能把 `Dockerfile` 当成 Shell 脚本来写：

```dockerfile
RUN cd /src/app
RUN java -jar app.jar
```

以上操作中第二行的工作目录并不是 `/src/app`，两个指令不在同一层，第一个 `RUN` 指令的 `cd` 操作和第二个没有任何关系。因此要切换目录，应该使用 `WORKDIR` 来指定。

## USER

`USER` 指令指定当前用户。与 `WORKDIR` 相似，会影响以后的层。`USER` 改变执行 `RUN`、`CMD` 和 `ENTRYPOINT` 的用户。格式：`USER <用户名>[:<用户组>]`。

`USER` 指定的用户和组必须是事先创建好的，否则无法切换。

```dockerfile
# 添加用户
RUN groupadd -r redis \
    && useradd -r -g redis redis
USER redis
ENTRYPOINT ["reids-server"]
```

## ONBUILD

`ONBUILD` 指令后面跟的是其它指令，它在当前镜像构建时不会被执行，只有以当前镜像为基础镜像去构建下一级镜像时才会被执行。格式：`ONBUILD <其它指令>`。

```dockerfile
FROM openjdk:8-jre-alpine
WORKDIR /app
ONBUILD COPY ./app.jar /app
...
```

这个 `Dockerfile` 在构建时不会执行 `ONBUILD`。

```dockerfile
FROM my-jre
...
```

假设之前构建的镜像名是 my-jre，以上 `Dockerfile` 构建镜像时，原来的 `ONBUILD` 将执行。
