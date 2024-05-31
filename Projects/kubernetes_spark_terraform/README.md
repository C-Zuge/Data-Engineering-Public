## Project
This project meant to use terraform to build an environment to deploy spark on EKS and also attach a s3 to store the files.

### Requirements
- Install Terraform
- Install AWS CLI
- Generete and Assign AWS credential (Access_key and Secret_key) (https://docs.aws.amazon.com/IAM/latest/UserGuide/security-creds.html)
  - use "aws configure" on terminal to do this easily (https://docs.aws.amazon.com/cli/latest/userguide/cli-authentication-user.html)

### Setup eksctl
```bash
ARCH=amd64
PLATFORM=$(uname -s)_$ARCH
curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$PLATFORM.tar.gz"
tar -xzf eksctl_$PLATFORM.tar.gz -C /tmp && rm eksctl_$PLATFORM.tar.gz
sudo mv /tmp/eksctl /usr/local/bin
```

### Configure Terraform and build env
```bash
# Initialize terraform
terraform init
# Apply modules on your aws account
terraform apply
# Configure kubectl to communicate with the EKS cluster (stored in ~/.kube/config)
aws eks --region $AWS_REGION update-kubeconfig --name $CLUSTER_NAME
```

### Create and Switch kubectl Context
```bash
# Check kubectl contexts
kubectl config get-contexts
# Switch between kubectl contexts
kubectl config use-context <context_name>
# Create new context
kubectl config set-context <context_name> --namespace=<namespace_name>
# Delete context
kubectl config delete-context <context_name>
```

### Setting up OIDC and IAM service account
```bash
# Get OIDC of your cluster
oidc_id=$(aws eks describe-cluster --name $CLUSTER_NAME --query "cluster.identity.oidc.issuer" --output text | cut -d '/' -f 5)
echo $oidc_id
# Check IAM OIDC already in your account
aws iam list-open-id-connect-providers | grep $oidc_id | cut -d "/" -f4
# Create a an IAM OIDC into your cluster
eksctl utils associate-iam-oidc-provider --cluster $CLUSTER_NAME --approve
# Create namespace inside your cluster
kubectl create namespace <namespace_name>
# Create service account or override otherwise
eksctl create iamserviceaccount \
--name spark \
--namespace <namespace_name> \
--cluster $CLUSTER_NAME \
--attach-policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess \
--approve \
--override-existing-serviceaccounts
# Authenticate login on helm registry
aws ecr get-login-password --region us-east-1 | helm registry login --username AWS --password-stdin 709825985650.dkr.ecr.us-east-1.amazonaws.com
```

### Spark Helm Install
```bash
helm install --namespace <namespace_name> \
    joom-spark-platform \
    oci://709825985650.dkr.ecr.us-east-1.amazonaws.com/joom/joom-spark-platform \
    --version 1.0.0
```

### Updating and Applying Spark Manifest
```bash
# Fetch manifest (make your changes on this file)
aws s3 cp s3://joom-analytics-cloud-public/examples/minimal/minimal-write.yaml minimal-write.yaml
## Apply on cluster
kubectl apply -f minimal-write.yaml 
# Check Logs
kubectl -n spark logs demo-minimal-write-driver -f
```

### Delete service account and enviroment
```bash
# Delete IAM SA
eksctl delete iamserviceaccount --name spark --namespace <namespace_name> --cluster $CLUSTER_NAME
# Delete env
terraform destroy
```

## Links
- https://www.youtube.com/watch?v=7wRqtBMS6E0
- https://www.sensedia.com.br/post/como-criar-cluster-kubernetes-com-terraform-e-aws-eks
- https://mateusmuller.me/posts/como-criar-cluster-eks-com-terraform/
- https://wangpp.medium.com/terraform-eks-nodegroups-with-custom-launch-templates-5b6a199947f
- https://cloud.joom.ai/spark-platform/getting-started