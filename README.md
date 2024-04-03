<p align="center">
  <a href="https://t.me/candy_uncle_bot">
    <img src="https://th.bing.com/th/id/OIG4.dbY3kumcxp.kAMN4P_kz?w=1024&h=1024&rs=1&pid=ImgDetMain" height="255px" alt="Candy Uncle">
  </a>
</p>
<p align="center">
    <em>Candy Uncle is a Telegram BOT as a PET project using the best practices of python application development that I have learned.</em>
</p>

[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)
[![Aiogram](https://img.shields.io/badge/aiogram-3.4.1-blue?style=plastic)](https://docs.aiogram.dev/en/dev-3.x/)
[![Celery](https://img.shields.io/badge/celery-5.4.0-green?style=plastic)](https://github.com/celery/celery)
![Linux (Ubuntu)](https://img.shields.io/badge/linux-ubuntu-green.svg)
[![Docker-compose](https://img.shields.io/badge/docker-compose-orange.svg)](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-22-04)


## Start

add `.env` file from `.env_example` template

- `ENVIRONMENT=DEVELOPMENT` should be 'TESTING', 'DEVELOPMENT' or 'PRODUCTION'
- `BOT_TOKEN=changeme` create bot with https://t.me/BotFather and get token
- `SUPERUSER_ID=310888528` - user id for logging and permission for config (get from https://t.me/userinfobot or debugging `message.from_user.id`)

webhooks settings
- `WEBHOOK_HOST=https://yourhost`
- `WEBHOOK_SECRET=changeme`
- `WEBHOOK_PATH=/candy_uncle/webhook`
- `WEB_SERVER_PORT=5601`
- `WEBHOOK_SSL_CERT=certificates/public_self-signed.pem`
- `WEBHOOK_SSL_PRIV=certificates/private_self-signed.key`

databases settings
- `POSTGRES_HOST=localhost`
- `POSTGRES_PORT=5432`
- `POSTGRES_USER=admin`
- `POSTGRES_PASSWORD=changeme`
- `POSTGRES_DB=candy_uncle_db`
- `REDIS_HOST=localhost`
- `REDIS_PORT=6379`
- `REDIS_PASSWORD=changeme`

for `DEVELOPMENT` run project
```bash
make dev
```

for `PRODUCTION`
change variables in `.env` file:
- IS_PROD=`True`
- POSTGRES_HOST=`postgres`
- REDIS_HOST=`redis`

and run BOT
```bash
make prod
```

<details>
<summary> <b>PREPARING FOR DEPLOYMENT GUIDE (VPS Ubuntu 22.04)</b></summary>
<br>

update package list and system utils
```bash
sudo apt update && sudo apt upgrade
```

configure ssl for git
```bash
ssh-keygen -t ed25519 -C "youremail@example.com"
```
enter to default path

add new key to https://github.com/settings/keys
```bash
cat ~/.ssh/id_ed25519.pub
```

download project
```bash
mkdir candy_uncle && cd candy_uncle
git init .
git remote add origin git@github.com:smile4alice/candy_uncle.git
git fetch
git switch main
```

#### Make
```bash
sudo apt install make
```

---
#### DOCKER
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04

-after install required command:
```bash
sudo usermod -aG docker ${USER}
```

#### DOCKER COMPOSE
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-22-04

after change usermod you need reboot system:
```bash
sudo reboot
```
---
#### NGINX
```bash
sudo apt install nginx
sudo ufw allow 'Nginx HTTP'
sudo ufw allow 'Nginx HTTPS'
sudo systemctl restart nginx
```

disable default config
```bash
sudo rm /etc/nginx/sites-enabled/default
```

#### CONFIGURE WEBHOOK

```bash
sudo nano /etc/nginx/sites-available/candy_uncle
```

save config from template:
```nginx
server {
    server_name default_server;

    listen 443 ssl;

    ssl_certificate     /etc/nginx/certificates/public_self-signed.pem;
    ssl_certificate_key /etc/nginx/certificates/private_self-signed.key;

    location /candy_uncle/webhook {
        proxy_pass http://127.0.0.1:5601;
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_redirect off;
        proxy_buffering off;
    }
}
```

enable it
```bash
sudo ln -s /etc/nginx/sites-available/candy_uncle /etc/nginx/sites-enabled/
```
---

#### SELF-SIGNED SSL
change `-subj ...`
```bash
sudo mkdir -p /etc/nginx/certificates/
sudo openssl req -newkey rsa:2048 -sha256 -nodes -keyout /etc/nginx/certificates/private_self-signed.key -x509 -days 365 -out /etc/nginx/certificates/public_self-signed.pem -subj "/C=US/ST=New York/L=Brooklyn/O=Example Brooklyn Company/CN=YOURDOMAIN.EXAMPLE"
```

copy it to project dirrectory
```bash
mkdir certificates
sudo cp /etc/nginx/certificates/*self-signed* certificates/
```

before run project
```bash
sudo systemctl restart nginx
```

for testing webhooks use GET 
`https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo`

</details>

## License
This project is licensed under the terms of the MIT license.
