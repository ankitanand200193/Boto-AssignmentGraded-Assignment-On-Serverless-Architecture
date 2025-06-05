# Boto-AssignmentGraded-Assignment-On-Serverless-Architecture

## EC2 Auto Start/Stop Lambda Function

Automatically manage EC2 instances based on tags using AWS Lambda.

### Setup

#### Create two EC2 instances:
   - Tag one as `Name: Auto-Stop-Ankit`
   - Tag other as `Name: Auto-Start-Ankit`

#### Create Lambda IAM role with EC2 permissions
1. Navigate to IAM Console:
   - Go to AWS Console → IAM → Roles → Create Role

2. Create Lambda Role:
   - Choose AWS Service as trusted entity
   - Select "Lambda" as use case
   - Click "Next"

3. Add Permissions:
   - Search for "AmazonEC2FullAccess"
   - Select the policy
   - Click "Next"

4. Configure Role:
   - Name: "boto-ankit-start-stop-ec2"
   - Description: "Allows Lambda to control EC2 instances"
   - Click "Create role"

#### Create Lambda function:
   - Use Python 3.x runtime
   - Assign IAM role

### Lambda Function

- Uses Boto3 to write a code that:
  - Describe tagged instances
  - Stop `Auto-Stop-Ankit` instances
  - Start `Auto-Start-Ankit` instances
  - Log affected instance IDs

- Deploy the code in Lambda

### Testing
1. Open Lambda Console:
   - Navigate to AWS Console → Lambda
   - Select your function

2. Test Tab:
   - Click "Test" tab
   - Click "Test" button
   OR
   - Click "Configure test event" if first time



