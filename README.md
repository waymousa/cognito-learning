# cognito-learning
This is a learning tool for examining how AWS Application Load Balancer, Cognito and a simpel python flask application ruhnning on EC2 interact so that you can learn about the authentication and authroisation flows.

The python application has 4 URI you can invoke:

/v1/public - a list of public data
/v1/secrets - a list of secret information that requires an authenticated user
/ - a default uri that displays a simple HTML page
/logout - a logout url that resets the ALB cookies

# Architecture

Diagram to do.

# Building the environment

First, create a VPC with a public and private subnet and a nat gateway.  Create an EC2 instance using the Amazon linux 2 image and pop it in the private subnet.  The EC2 instance should be managed by Systems manager and have the agent installed and running.  Ensure that you can use session manager to access the EC2 instance and that the instance can reach the internet.  The instance will also need a role that can write to CloudWatch.

Under the ec2-user home directory, install Python3 then create a venv environment.  Switch to the venv environment and upgrade pip.  Next, install the python packages flask, watchtower and waitress.

Create a target group using HTTP on port 5000.  Create an Application Load Balancer listening on port 80 and routing to he target group.  Lastly, create a Cloudwatch agent log group and stream.

Fork this github repo to a new copy and switch to it.  Set up a deployment pipeline using your new github repo as the source, skip the build step and create a deployment to an EC2/On-prem instance.  The appspec.yml is already created and should work when the pipeline runs.

All things beign equal, you should now have a python app runinng in a waitress container lisening on port 5000.  The target group should update and the application load balancer become active.  Check that the /, /v1/public and /v1/secret uri's are all working.  The logs whould be goign to CloudWatch and the server.log in the ec2-user's home directory.

Next, set up DNS in Route 53 for your site.  Set up an SSl certificate for the site then create an https listener.  Set up http to forward to https on the ALB.  Set up Cognito to use a user pool and create application url redirects and logout url.  Edit the code in the app.py to take account fo the new DNS name for your site.  Just search and replace the hostname par of any URL contained in the code.  Lastly, set up a new rule in the ALB to resuire authentication for /v1/secrets path, and use your newly created Cognito application as the target.  Forward the traffic to the target group if the logon is sucessful.

Now try the site again and this time you should see a logon page when you try to access the secrets page.  When loggedn in, you should see all the tokens in the CloudWatch logs.  you can grab them from thewir to decode them if you like or add more logging code to do that.

Next try the /logout link on the home page.  This will invoke the logout endpoint for Cognito as well as running the logout api on the server which invalidates the ALB cookies.  Check that the cookies have expired and that you are required to logon again should you see the /v1/secrets page.

Note that it is possible to invalidate the cookies using the /logout api call without first invoking the COgnito logout endpoint.  This doesn't really log you out and on the next run to the /v1/secrets page you will get a new cookie from the ALB!

# OAuth authentication flow

To do.