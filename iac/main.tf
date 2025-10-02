terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

resource "docker_image" "ml_image" {
  name = "mycustom/ml-image:latest"
}

resource "docker_container" "ml_container" {
  name  = "ml_training"
  image = docker_image.ml_image.name

  ports {
    internal = 8888
    external = 8888
  }

  ports {
    internal = 5000
    external = 5000
  }

  volumes {
    host_path      = "/home/samuel/mlflow_data"   # chemin sur la machine hôte à créer
    container_path = "/mlflow"
  }

  volumes {
    host_path      = "/home/samuel/dev/ingenieuria/projet7"
    container_path = "/root/work"
  }

  volumes {
    host_path      = "/home/samuel/dev/ingenieuria/projet7/input"
    container_path = "/root/work/input"
  }

  restart = "unless-stopped"
}
