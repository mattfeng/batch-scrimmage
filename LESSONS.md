# Lessons Learned

* **AWS security settings between services needs to be set correctly.**
    * AWS EC2 instance cannot connect to AWS RDS unless the security rules on the AWS RDS permits connection from that IP (by default, only machines in AWS RDS security group can cannot, which is generally no computers).