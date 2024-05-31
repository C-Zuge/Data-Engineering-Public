resource "aws_ecr_repository" "manager" {
  name                 = "dev/spark-kube-repo"
  image_tag_mutability = "MUTABLE"
  force_delete = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags ={
    proj = "spark-kube"
  }
}