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
  name         = "mycustom/ml-image:latest"
  keep_locally = true # Empêche Terraform de supprimer l'image si elle n'est plus utilisée par un conteneur
  build {
    context = "."
  }
}

resource "docker_container" "ml_container" {
  name  = "ml_training"
  # Utilise l'ID de l'image (hash SHA256) au lieu du tag.
  # Cela garantit que le conteneur est recréé si l'image change.
  image = docker_image.ml_image.id

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
