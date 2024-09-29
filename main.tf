terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {}

resource "docker_image" "app_image" {
  name = "test:latest"
  build {
    context    = "./"
    dockerfile = "Dockerfile"
  }
}

resource "docker_container" "app_container" {
  name  = "test_container"
  image = docker_image.app_image.name  # Change this line to use 'name'
  
  ports {
    internal = 8001
    external = 8001
  }

  env = [
    "FLASK_APP=main.py",
    "FLASK_ENV=development"
  ]

  restart = "unless-stopped"
}

