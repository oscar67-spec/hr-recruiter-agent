# deploy.ps1 — Deploy HR Recruiter Slack Lambda functions to AWS
# Run from: app/HRRecruiterAgent/slack_lambda/
# Usage: .\deploy.ps1

$ErrorActionPreference = "Stop"

# ── Config ─────────────────────────────────────────────────────────────────────
$env:AWS_PROFILE  = "chidiadioscar3"
$REGION           = "us-east-1"
$ACCOUNT          = "416291742983"
$RUNTIME_ARN      = "arn:aws:bedrock-agentcore:us-east-1:416291742983:runtime/HRRecruiterAgentNew_HRRecruiterAgent-L54zkOCNQx"

$RECEIVER_NAME    = "hr-slack-receiver"
$WORKER_NAME      = "hr-slack-worker"
$ROLE_NAME        = "hr-slack-lambda-role"
$ROLE_ARN         = "arn:aws:iam::${ACCOUNT}:role/${ROLE_NAME}"

# Tokens — set these as environment variables before running, do NOT hardcode
# export SLACK_BOT_TOKEN=xoxb-...
# export SLACK_SIGNING_SECRET=...
$SLACK_BOT_TOKEN      = $env:SLACK_BOT_TOKEN
$SLACK_SIGNING_SECRET = $env:SLACK_SIGNING_SECRET

if (-not $SLACK_BOT_TOKEN -or -not $SLACK_SIGNING_SECRET) {
    Write-Host "ERROR: Set SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET environment variables first." -ForegroundColor Red
    exit 1
}

Write-Host "`n=== HR Slack Lambda Deployment ===" -ForegroundColor Cyan

# ── Step 1: Create IAM role (skip if exists) ───────────────────────────────────
Write-Host "`n[1/6] Setting up IAM role..." -ForegroundColor Yellow

$trustPolicy = @{
    Version   = "2012-10-17"
    Statement = @(@{
        Effect    = "Allow"
        Principal = @{ Service = "lambda.amazonaws.com" }
        Action    = "sts:AssumeRole"
    })
} | ConvertTo-Json -Depth 5

$roleExists = aws iam get-role --role-name $ROLE_NAME --profile chidiadioscar3 2>$null
if (-not $roleExists) {
    aws iam create-role `
        --role-name $ROLE_NAME `
        --assume-role-policy-document $trustPolicy `
        --profile chidiadioscar3 | Out-Null
    Write-Host "  Created IAM role: $ROLE_NAME"
} else {
    Write-Host "  IAM role already exists: $ROLE_NAME"
}

# Attach policies
aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole" --profile chidiadioscar3 2>$null
aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn "arn:aws:iam::aws:policy/AmazonBedrockFullAccess" --profile chidiadioscar3 2>$null

# Inline policy: allow invoking the worker Lambda
$lambdaPolicy = @{
    Version   = "2012-10-17"
    Statement = @(@{
        Effect   = "Allow"
        Action   = "lambda:InvokeFunction"
        Resource = "arn:aws:lambda:${REGION}:${ACCOUNT}:function:${WORKER_NAME}"
    })
} | ConvertTo-Json -Depth 5

aws iam put-role-policy `
    --role-name $ROLE_NAME `
    --policy-name "InvokeWorkerLambda" `
    --policy-document $lambdaPolicy `
    --profile chidiadioscar3 | Out-Null

Write-Host "  Policies attached."
Write-Host "  Waiting 10s for IAM role to propagate..."
Start-Sleep -Seconds 10

# ── Step 2: Package Lambda code ────────────────────────────────────────────────
Write-Host "`n[2/6] Packaging Lambda functions..." -ForegroundColor Yellow

$PACKAGE_DIR = "$PSScriptRoot\package"
if (Test-Path $PACKAGE_DIR) { Remove-Item -Recurse -Force $PACKAGE_DIR }
New-Item -ItemType Directory -Path $PACKAGE_DIR | Out-Null

# Install dependencies into package/
pip install -r "$PSScriptRoot\requirements.txt" -t $PACKAGE_DIR --quiet

# ── Step 3: Deploy Receiver Lambda ─────────────────────────────────────────────
Write-Host "`n[3/6] Deploying receiver Lambda..." -ForegroundColor Yellow

Copy-Item "$PSScriptRoot\receiver.py" "$PACKAGE_DIR\receiver.py"

Compress-Archive -Path "$PACKAGE_DIR\*" -DestinationPath "$PSScriptRoot\receiver.zip" -Force

$receiverExists = aws lambda get-function --function-name $RECEIVER_NAME --profile chidiadioscar3 2>$null
if (-not $receiverExists) {
    aws lambda create-function `
        --function-name $RECEIVER_NAME `
        --runtime python3.12 `
        --role $ROLE_ARN `
        --handler receiver.handler `
        --zip-file "fileb://$PSScriptRoot\receiver.zip" `
        --timeout 10 `
        --environment "Variables={SLACK_SIGNING_SECRET=$SLACK_SIGNING_SECRET,WORKER_FUNCTION_NAME=$WORKER_NAME}" `
        --profile chidiadioscar3 | Out-Null
    Write-Host "  Created: $RECEIVER_NAME"
} else {
    aws lambda update-function-code `
        --function-name $RECEIVER_NAME `
        --zip-file "fileb://$PSScriptRoot\receiver.zip" `
        --profile chidiadioscar3 | Out-Null
    aws lambda update-function-configuration `
        --function-name $RECEIVER_NAME `
        --environment "Variables={SLACK_SIGNING_SECRET=$SLACK_SIGNING_SECRET,WORKER_FUNCTION_NAME=$WORKER_NAME}" `
        --profile chidiadioscar3 | Out-Null
    Write-Host "  Updated: $RECEIVER_NAME"
}

Remove-Item "$PACKAGE_DIR\receiver.py"

# ── Step 4: Deploy Worker Lambda ───────────────────────────────────────────────
Write-Host "`n[4/6] Deploying worker Lambda..." -ForegroundColor Yellow

Copy-Item "$PSScriptRoot\worker.py" "$PACKAGE_DIR\worker.py"

Compress-Archive -Path "$PACKAGE_DIR\*" -DestinationPath "$PSScriptRoot\worker.zip" -Force

$workerExists = aws lambda get-function --function-name $WORKER_NAME --profile chidiadioscar3 2>$null
if (-not $workerExists) {
    aws lambda create-function `
        --function-name $WORKER_NAME `
        --runtime python3.12 `
        --role $ROLE_ARN `
        --handler worker.handler `
        --zip-file "fileb://$PSScriptRoot\worker.zip" `
        --timeout 180 `
        --environment "Variables={SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN,AGENTCORE_RUNTIME_ARN=$RUNTIME_ARN}" `
        --profile chidiadioscar3 | Out-Null
    Write-Host "  Created: $WORKER_NAME"
} else {
    aws lambda update-function-code `
        --function-name $WORKER_NAME `
        --zip-file "fileb://$PSScriptRoot\worker.zip" `
        --profile chidiadioscar3 | Out-Null
    aws lambda update-function-configuration `
        --function-name $WORKER_NAME `
        --environment "Variables={SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN,AGENTCORE_RUNTIME_ARN=$RUNTIME_ARN}" `
        --profile chidiadioscar3 | Out-Null
    Write-Host "  Updated: $WORKER_NAME"
}

# ── Step 5: Create API Gateway (HTTP API) ──────────────────────────────────────
Write-Host "`n[5/6] Setting up API Gateway..." -ForegroundColor Yellow

$RECEIVER_ARN = "arn:aws:lambda:${REGION}:${ACCOUNT}:function:${RECEIVER_NAME}"

# Check if API already exists
$existingApis = aws apigatewayv2 get-apis --profile chidiadioscar3 | ConvertFrom-Json
$api = $existingApis.Items | Where-Object { $_.Name -eq "hr-slack-api" }

if (-not $api) {
    $apiResult = aws apigatewayv2 create-api `
        --name "hr-slack-api" `
        --protocol-type HTTP `
        --target $RECEIVER_ARN `
        --profile chidiadioscar3 | ConvertFrom-Json

    $API_ID       = $apiResult.ApiId
    $API_ENDPOINT = $apiResult.ApiEndpoint

    # Allow API Gateway to invoke receiver Lambda
    aws lambda add-permission `
        --function-name $RECEIVER_NAME `
        --statement-id "AllowAPIGateway" `
        --action lambda:InvokeFunction `
        --principal apigateway.amazonaws.com `
        --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT}:${API_ID}/*" `
        --profile chidiadioscar3 | Out-Null

    Write-Host "  Created API Gateway: $API_ID"
} else {
    $API_ID       = $api.ApiId
    $API_ENDPOINT = $api.ApiEndpoint
    Write-Host "  API Gateway already exists: $API_ID"

    # Re-add permission in case receiver Lambda was recreated
    aws lambda add-permission `
        --function-name $RECEIVER_NAME `
        --statement-id "AllowAPIGateway" `
        --action lambda:InvokeFunction `
        --principal apigateway.amazonaws.com `
        --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT}:${API_ID}/*" `
        --profile chidiadioscar3 2>$null | Out-Null
}

# ── Step 6: Cleanup temp files ─────────────────────────────────────────────────
Write-Host "`n[6/6] Cleaning up..." -ForegroundColor Yellow
Remove-Item -Recurse -Force $PACKAGE_DIR -ErrorAction SilentlyContinue
Remove-Item "$PSScriptRoot\receiver.zip" -ErrorAction SilentlyContinue
Remove-Item "$PSScriptRoot\worker.zip" -ErrorAction SilentlyContinue

# ── Done ───────────────────────────────────────────────────────────────────────
Write-Host "`n=== Deployment Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Your Slack Event URL:" -ForegroundColor Cyan
Write-Host "  $API_ENDPOINT/slack/events" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Go to https://api.slack.com/apps"
Write-Host "  2. Click your app -> Event Subscriptions"
Write-Host "  3. Enable Events and paste the URL above"
Write-Host "  4. Subscribe to: app_mention, message.im"
Write-Host "  5. Save Changes"
