terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "us-east-1"
}

module "ecr" {
  source = "./modules/ecr"
}

module "eks" {
  source = "./modules/eks"
  cluster_name = "airflow-eks-cluster"

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = { 
      most_recent = true
      service_account_role_arn = module.eks.airflow_service_account_role.arn
      resolve_conflicts="PRESERVE"
    }
  }
}

module "s3" {
  source = "./modules/s3"
}

module "rds" {
  source = "./modules/rds"
  db_username = var.db_username
  db_password = var.db_password
}

resource "kubernetes_namespace" "airflow" {
  metadata {
    name = "airflow"
  }
  depends_on = [module.eks]
}

resource "kubernetes_service_account" "airflow_service_account" {
  metadata {
    name      = "airflow"
    namespace = kubernetes_namespace.airflow.metadata[0].name
    annotations = {
      "eks.amazonaws.com/role-arn" = module.eks.airflow_service_account_role.arn
    }
  }
  depends_on = [module.eks]
}

resource "kubernetes_persistent_volume" "pv_airflow" {
  metadata {
    name = "airflowpv"
  }
  spec {
    capacity = {
      storage = "20Gi"
    }
    access_modes = ["ReadWriteMany"]
    persistent_volume_source {
      aws_elastic_block_store {
        volume_id = module.ebs.ebs_infos.id
      }
    }
  }
  depends_on = [module.eks]
}