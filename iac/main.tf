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

data "docker_image" "ml_image" {
  name = "mycustom/ml-image:latest"
}

resource "docker_container" "ml_container" {
  name  = "ml_training"
  image = data.docker_image.ml_image.name

  # Ajout d'une variable d'environnement pour forcer la recréation du conteneur
  # lorsque l'ID de l'image change.
  env = ["IMAGE_ID=${data.docker_image.ml_image.id}"]

  ports {
    internal = 8888
    external = 8888
  }

  ports {
    internal = 5000
    external = 5000
  }

  ports {
    internal = 8000
    external = 8000
  }

  volumes {
    host_path      = "${path.cwd}/mlflow_data"   # chemin sur la machine hôte à créer
    container_path = "/mlflow"
  }

  volumes {
    host_path      = path.cwd
    container_path = "/root/work"
  }

  volumes {
    host_path      = "${path.cwd}/input"
    container_path = "/root/work/input"
  }

  restart = "unless-stopped"
}
