### Welcome to my New York City Taxi Count Predictor Web App
In this project, I wanted to deploy my taxi count predictor model using Django.

# Summary of Django Process:
- Firstly, I designed a an ERM (Entity Relationship Model) database and implemented necessary models.
- I upload my taxi count predictor.
- I did the necessary signal functions to be triggered when a taxi driver enter a new instance.
- Different user types (Admin, Taxi Driver, Regular User) implemented.
- Generic based views implemented and set the connection between HTML pages
- Finally, the project is dockerized.

## Docker ile Çalıştırma

Proje Docker Hub üzerinden yayınlanmıştır: [DOCKER_HUB_LINKI](https://hub.docker.com/repository/docker/tahasoylu44/nyc-taxi-prediction/)

### Image'ı çekmek için:
​```bash
docker pull tahasoylu44/nyc-taxi-prediction:v1
​```

### Docker Compose ile (varsa):
​```bash
docker-compose up -d
​```

Uygulama ayağa kalktıktan sonra tarayıcıdan şu adrese giderek erişebilirsin:
​```
http://localhost:8000/predict
​```