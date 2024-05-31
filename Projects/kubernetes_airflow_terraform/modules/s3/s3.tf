resource "aws_s3_bucket" "airflow_bucket" {
  bucket        = "kube-airflow-bucket"
  force_destroy = true

  tags = {
    Environment = "prod-airflow-kube"
  }
}

resource "aws_s3_bucket_public_access_block" "airflow_bucket" {
  bucket = aws_s3_bucket.airflow_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}