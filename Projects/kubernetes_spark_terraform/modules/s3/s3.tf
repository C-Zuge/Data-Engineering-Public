resource "aws_s3_bucket" "spark_bucket" {
  bucket        = "kube-spark-bucket"
  force_destroy = true

  tags = {
    spark = "spark-kube"
  }
}

resource "aws_s3_bucket_public_access_block" "spark_bucket" {
  bucket = aws_s3_bucket.spark_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}