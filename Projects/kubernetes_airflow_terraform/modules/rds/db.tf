terraform {
  required_providers {
    postgresql = {
      source = "cyrilgdn/postgresql"
      version = "1.22.0"
    }
  }
}

resource "aws_security_group" "rds_sg" {
  name = "rds_sg"
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "prod-airflow-rds-postgres-instance" {
  engine                 = "postgres"
  identifier             = "prod-airflow-kube-db"
  allocated_storage      = 20
  engine_version         = "15.6"
  instance_class         = "db.m5d.large"
  username               = var.db_username
  password               = var.db_password
  parameter_group_name   = "default.postgres15"
  vpc_security_group_ids = ["${aws_security_group.rds_sg.id}"]
  skip_final_snapshot    = true
  publicly_accessible    = true
}

# resource "null_resource" "db_init" {
#   depends_on = [aws_db_instance.prod-airflow-rds-postgres-instance]

#   provisioner "local-exec" {
#     command = "sudo apt-get install postgresql-client -y && psql -h ${replace(aws_db_instance.prod-airflow-rds-postgres-instance.endpoint, ":5432", "")} -p 5432 -U ${var.db_username} -W ${var.db_password} < ./modules/rds/start-db.sql"
#   }
# }

# Setup PostgreSQL Provider After RDS Database is Provisioned
provider "postgresql" {
    host            = "${aws_db_instance.prod-airflow-rds-postgres-instance.address}"
    port            = 5432
    username        = "postgres"
    password        = "postgres"
    superuser       = false
}
# Create App User
resource "postgresql_role" "application_role" {
    name                = "airflow_tmp"
    login               = true
    password            = "postgres"
    encrypted_password  = true
    superuser           = false
    depends_on          = [aws_db_instance.prod-airflow-rds-postgres-instance]
}
# Create Database 
resource "postgresql_database" "dev_db" {
    name              = "airflow"
    owner             = "postgres"
    template          = "template0"
    lc_collate        = "C"
    connection_limit  = -1
    allow_connections = true
    depends_on        = [aws_db_instance.prod-airflow-rds-postgres-instance]
}

output "rds_endpoint" {
  value = aws_db_instance.prod-airflow-rds-postgres-instance.endpoint
}