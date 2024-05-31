# resource "aws_launch_template" "eks_node_launch_template" {
#   name   = "eks-node-template-spark"
#   image_id      = "ami-04b70fa74e45c3917"  # Ubuntu-22.04 LTS us-east-1
#   vpc_security_group_ids = [aws_security_group_rule.eks_sg_ingress_rule.security_group_id, aws_eks_cluster.cluster.vpc_config[0].cluster_security_group_id]

#   block_device_mappings {
#     device_name = "/dev/xvda"

#     ebs {
#       volume_size = 20
#       volume_type = "gp2"
#     }
#   }

#   # Specify the EKS optimized AMI ID for the region and Kubernetes version
#   metadata_options {
#     http_endpoint = "enabled"
#     http_tokens = "required"
#   }

#   # Specify the shell script to be executed when the instance is launched
#   user_data = base64encode(<<-EOF
# #!/bin/bash
# echo "Updating helm"
# helm repo update
# echo "Installing spark operator (ignore name in use error)"
# helm install my-spark-operator spark-operator/spark-operator  --create-namespace --namespace spark-operator --set webhook.enable=true || true
# echo "Creating spark service account (ignore already exists error)"
# kubectl create serviceaccount spark || true
# kubectl create clusterrolebinding spark-role --clusterrole=edit --serviceaccount=default:spark --namespace=default || true
#   EOF
#   )
  
#   # Specify the tags for the Launch Template
#   tag_specifications {
#     resource_type = "instance"
#     tags = {
#       Name        = "eks-node"
#       Environment = "production"
#     }
#   }

#    depends_on = [
#     aws_eks_cluster.cluster,
#     aws_security_group_rule.eks_sg_ingress_rule
#   ]
# }