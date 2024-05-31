output "aws_subnet" {
    value = {
        "subnet_private_1a": aws_subnet.subnet_private_1a.id,
        "subnet_private_1b": aws_subnet.subnet_private_1b.id,
    }
}

output "eks_cluster" {
    value = {
        "cluster": aws_eks_cluster.cluster,
        "endpoint": aws_eks_cluster.cluster.endpoint,
        "certificate_auth_data": aws_eks_cluster.cluster.certificate_authority[0].data,
        "oidc_issuer": aws_eks_cluster.cluster.identity[0].oidc[0].issuer
    }
}
output "spark_service_account_role" {
  value = {
        "arn": aws_iam_role.spark_service_account_role.arn
    }
}
output "node_group_infos" {
  value = {
        "resources": aws_eks_node_group.eks_node_group.resources
    }
}