# AWS RDS and Lambda Integration with S3 Event Trigger

This README will guide you through the process of setting up an Amazon RDS instance, creating Lambda functions, and setting up an S3 bucket to trigger one of the Lambda functions. This entire pipeline allows for automatic data processing whenever new data is uploaded to S3.

## Prerequisites

1. **AWS Account**
2. **Python**: We'll be using Python 3.11 for our Lambda function
3. **pip**: Ensure you have pip installed. It's typically included with recent versions of Python.
4. **MySQL Client**: For connecting to the RDS database. You can use MySQL Workbench

## Initial Setup
## 1. Configuring RDS (Relational Database Service)

### Database Creation
- Login to AWS Console
- First create RDS instance
- Navigate to RDS in the AWS Console.
- Choose the desired database (MySQL) and configure the instance details.
- Set up a master username and password. Securely store these credentials.
- Make the database publicly available (or you wont be able to access it via MySQL client later)

### Database Configuration

- Modify the default VPC security group to allow all inbound traffic on the database port(3306).
- Note down the RDS endpoint. It'll be used later.

### Database Tables Setup

- Connect to the database using MySQL Workbench.
- Create the necessary database and tables for storing data (refer to "useful sql commands.txt" file).

## 2. Setting Up IAM (Identity and Access Management)

    ### Role Creation

    - Navigate to the IAM dashboard.
    - Create a new role for AWS services and select Lambda.

    ### Attaching Policies

    - Attach policies granting RDS, S3 and CloudWatch full access.

## 3. Creating an S3 Bucket

        ### Bucket Creation

        - Navigate to the S3 dashboard.
        - Create a new bucket, ensuring it has a unique name (name is "acmecorpfunctions").
        - Create a folder inside your S3 bucket name it "data" this is where you'll upload your sample data

## 4. Setting Up Lambda Functions

        ### Function Creation ()

        ## read_s3_to_rds function
        - lambda function to load data from s3 to RDS (give it the name "read-s3-to-rds")
        - Navigate to the Lambda dashboard.
        - Create a new function and assign the IAM role created in step 2.

        ## retrieve_rds_data function
        - lambda function to retrieve specfic data from rds (give it the name "retrieve_rds_data")
        - Navigate to the Lambda dashboard.
        - Create a new function and assign the IAM role created in step 2.
        - Use json payload to manually trigger the function during a test (refer to jsonPayload.txt). i.e click on the test tab within the lambda function

        ### Environment Configuration

        - Set up your RDS credentials as environment variables on the both the lambda functions. ( configuration tab -> Environment variables )
  
## 5. S3 Event Trigger (only to be done for read-s3-to-rds lambda function )

        ### Event Setup

        - On the lambda function create in step 4, select add trigger , select S3 as a source
        - Select the bucket name we created in step 3
        - Event type must be ("All object create events")
        - Prefix is the folder created in step 3 ("/data")
        - Suffix (".txt") this will allow only .txt files to trigger the function (this is due to our data stored in a txt file)
        - check the acknowledgement option and click add event

        ## Running the Code

        1. **Clone the repository**:
        ```bash
        git clone [REPOSITORY_LINK]
        ```

        2. **Install Dependencies**:
        ```bash
        pip install -r requirements.txt
        ```
        ## Testing the Setup

        1. Upload a new file to the S3 bucket.
        2. The Lambda function should automatically process the data.
        3. Verify the data in RDS using MySQL Workbench.

## 6. Continuous Integration and Deployment (CI/CD) Workflow

        ### GitHub Actions

        The CI/CD pipeline is managed using GitHub Actions. This workflow automates the deployment of your Lambda functions whenever you push code to the "master" branch.

        ### Setting Up GitHub Secrets

        Before you run the pipeline, ensure you have set up the necessary secrets in your GitHub repository:

        1. Navigate to your GitHub repository.
        2. Click on the "Settings" tab.
        3. In the left sidebar, click on "Secrets".
        4. Add the following secrets:
        - "AWS_ACCESS_KEY_ID": Your AWS access key.
        - "AWS_SECRET_ACCESS_KEY": Your AWS secret key.

        ### Workflow Steps

        1. **Check out the code**: This will fetch the most recent code from the `master` branch.
        
        2. **Set up Python**: We're using Python 3.11 for this project.

        3. **Run unit tests**: Before deploying, the code will be tested to ensure that there are no regressions.

        4. **Install dependencies**: All required Python libraries will be installed and packaged for deployment.

        5. **Package dependencies for AWS Lambda Layer**: Layers allow you to manage your in-project dependencies separately, providing cleaner organization and reduced deployment sizes.

        6. **Configure AWS Credentials**: This will use the credentials from GitHub secrets to authenticate with AWS.

        7. **Upload data to S3**: If there's any example or test data, it's uploaded to your S3 bucket.

        8. **Publish a new version of Lambda Layer**: This step will publish a new version of your Lambda Layer containing dependencies.

        9. **Update Lambda function with new Layer**: The existing Lambda functions (both 'Retrieve' and 'Read') will be updated to use the latest version of the layer.

        10. **Upload Lambda function code**: The latest code for your Lambda functions will be zipped and uploaded.

        ### Running the CI/CD Pipeline

        1. Make sure you've committed all your changes.
        2. Push the changes to the "master" branch:
        ```bash
        git push origin master
        ```

        3. The pipeline will automatically trigger upon a push to the "master" branch.
        4. Navigate to the "Actions" tab in your GitHub repository to monitor the progress of the pipeline.
        5. If all steps are successful, your changes have been deployed to AWS. If there are any failures, use the logs provided in the GitHub Actions output to diagnose and correct the issue.


        With this setup, you have a fully automated workflow to ensure that every change pushed to the "master" branch is tested and deployed to AWS seamlessly. Remember to always validate changes in a separate environment (e.g., staging) before pushing to "master" to ensure the quality and stability of the production environment.