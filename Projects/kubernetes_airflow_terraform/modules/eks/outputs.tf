output "aws_subnet" {
    value = {
        "subnet_private_1a": aws_subnet.subnet_private_1a.id,
        "subnet_private_1b": aws_subnet.subnet_private_1b.id,
    }
}

output "eks_cluster" {
    value = aws_eks_cluster.cluster
}

output "node_group_infos" {
  value = {
        "resources": aws_eks_node_group.eks_node_group.resources
    }
}