terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "us-east-1"
}

provider "kubernetes" {
  host                   = module.eks.eks_cluster.endpoint
  token                  = data.aws_eks_cluster_auth.spark_cluster_auth.token
  cluster_ca_certificate = base64decode(module.eks.eks_cluster.certificate_auth_data)
}

module "ecr" {
  source = "./modules/ecr"
}

module "ebs"{
  source = "./modules/ebs"
}

module "eks" {
  source = "./modules/eks"
  cluster_name = "spark-eks-cluster"

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
      service_account_role_arn = module.eks.spark_service_account_role.arn
      resolve_conflicts="PRESERVE"
    }
  }
  depends_on = [ module.ebs ]
}

module "s3" {
  source = "./modules/s3"
}

resource "kubernetes_namespace" "spark" {
  metadata {
    name = "spark"
  }
  depends_on = [module.eks]
}

resource "kubernetes_service_account" "spark_service_account" {
  metadata {
    name      = "spark"
    namespace = kubernetes_namespace.spark.metadata[0].name
    annotations = {
      "eks.amazonaws.com/role-arn" = module.eks.spark_service_account_role.arn
    }
  }
  depends_on = [module.eks]
}

resource "kubernetes_persistent_volume" "pv_spark" {
  metadata {
    name = "sparkpv"
  }
  spec {
    capacity = {
      storage = "10Gi"
    }
    access_modes = ["ReadWriteMany"]
    persistent_volume_source {
      aws_elastic_block_store {
        volume_id = module.ebs.ebs_infos.id
      }
    }
  }
  depends_on = [module.ebs, module.eks]
}
data "aws_eks_cluster_auth" "spark_cluster_auth" {
  # aws_eks_cluster_auth is needed to bring the information of token and cluster name as object because module.eks.cluster_name is treated as string 
  name = module.eks.cluster_name
}