# Creating key-pair on AWS using SSH-public key
resource "aws_key_pair" "deployer" {
  key_name   = "key_pair_kube"
  public_key = file("/mnt/c/Repos/Data-Engineering/Projects/kubernetes_spark_terraform/ec2_key_pair.pub")
}

resource "aws_eks_node_group" "eks_node_group" {
  cluster_name    = aws_eks_cluster.cluster.name
  node_group_name = "spark-eks-cluster-node-group"
  node_role_arn   = aws_iam_role.eks_node_role.arn

  subnet_ids = [
    aws_subnet.subnet_public_1a.id,
    aws_subnet.subnet_public_1b.id
  ]

  # capacity_type  = "ON_DEMAND"
  capacity_type  = "SPOT"
  instance_types = ["t3.large"]
  disk_size = 50

  scaling_config {
    desired_size = 1
    max_size     = 3
    min_size     = 1
  }

  # remote_access {
  #   ec2_ssh_key = aws_key_pair.deployer.key_name  
  # }

  depends_on = [
    aws_iam_role_policy_attachment.eks_AmazonEKSWorkerNodePolicy,
    aws_iam_role_policy_attachment.eks_AmazonEKS_CNI_Policy,
    aws_iam_role_policy_attachment.eks_AmazonEC2ContainerRegistryReadOnly,
    aws_iam_role_policy_attachment.eks_AmazonEBSCSIDriverPolicy,
  ]

  lifecycle {
    create_before_destroy = true
  }
}