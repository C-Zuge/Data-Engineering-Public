resource "aws_ebs_volume" "ebs_volume" {
  availability_zone = "us-east-1a"
  size              = 10

  tags = {
    Name = "EBS_VOL"
  }
}

output "ebs_infos" {
  value = {
    "id": aws_ebs_volume.ebs_volume.id
    "arn": aws_ebs_volume.ebs_volume.arn
  }
}