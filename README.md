# 软件工程 智慧海洋牧场系统

- 2025NKU软件工程 8组

## 项目介绍

## 部署说明

### 前端部署说明

### 后端部署说明

#### 配置文件

在 `backend` 目录下创建 `config.ini` 文件，然后在文件内以如下格式(括号内仅为说明，无需写入ini文件)写入本地数据库配置：

```ini
[database]
user = root(你的数据库用户名)
password = xxxxxx(你的数据库密码)
host = localhost(默认地址，如有变动请修改)
port = 3306(默认端口，如有变动请修改)
```

#### 基础依赖

包括 Django REST 框架 、JWT 身份认证 框架 、MySQL 连接库等，具体安装部分见 "安装/运行命令"

#### 数据库相关

通过生成数据库迁移、执行数据库迁移，Django 会自动生成相关数据库表，所以数据库表的初始化在 Django 这里实现即可，具体实现见"安装/运行命令"

Django 会在 `projectdatabase` 数据库里生成相关的表，表名为 `appname_tablename`，比如 `user` app 的 `User` 模型就会被命名为 `user_user`，以此类推

#### 安装/运行命令

1. 切换目录

    ```shell
    cd backend
    ```

2. 安装依赖

    ```shell
    pip install djangorestframework
    pip install djangorestframework-simplejwt
    pip install mysqlclient
    pip install requests
    pip install scikit-learn
    pip install pandas
    pip install joblib
    pip install openai
    pip install zhipuai
    ```

3. 执行数据库迁移

    ```shell
    python manage.py makemigrations
    python manage.py migrate
    ```

4. 运行后端

    ```shell
    python manage.py runserver
    ```

### 数据库部署说明
