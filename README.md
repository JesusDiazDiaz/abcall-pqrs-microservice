
# Get token for testing
```bash
aws cognito-idp admin-initiate-auth --user-pool-id us-east-1_YDIpg1HiU --client-id 65sbvtotc1hssqecgusj1p3f9g --auth-flow ADMIN_NO_SRP_AUTH --auth-parameters USERNAME=robert@mail.com,PASSWORD=Test@123 --query 'AuthenticationResult.IdToken' --output text
```

```bash
chalice generate-pipeline --pipeline-version v2 --source github --buildspec-file buildspec.yml pipeline.json
aws cloudformation deploy --template-file pipeline.json --stack-name users-service-pipeline-stack --parameter-overrides GithubOwner=JesusDiazDiaz GithubRepoName=abcall-users-microservice --capabilities CAPABILITY_IAM
```

```bash
chalice package --merge-template extras.json out

aws cloudformation package \
     --template-file out/sam.json \
     --s3-bucket infra-abc \
     --output-template-file out/packaged-app/packaged.yaml

aws cloudformation deploy \
    --template-file out/packaged-app/packaged.yam[dto.py](chalicelib/src/modules/infrastructure/dto.py)l \
    --stack-name pqrs-service-stack \
    --capabilities CAPABILITY_IAM

```

# Run local using chalice local
```bash
python3 -m venv .venv
pip install -r requirements.txt
docker run --name my-postgres -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=mydb -p 5432:5432 -d postgres
export DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/mydb
chalice local
```