# cognito-learning
This is a learning tool for examining how AWS Application Load Balancer, Cognito and a simple python flask application running on EC2 interact so that you can learn about the authentication and authorisation flows.

The python application has 4 URI you can invoke:

/v1/public - a list of public data
/v1/secrets - a list of secret information that requires an authenticated user
/ - a default uri that displays a simple HTML page
/logout - a logout url that resets the ALB cookies

# Architecture

![Architecture Diagram](cognito-learning.jpg "Architecture diagram")

# Building the environment

First, create a VPC with a public and private subnet and a nat gateway.  Create an EC2 instance using the Amazon linux 2 image and pop it in the private subnet.  The EC2 instance should be managed by Systems manager and have the agent installed and running.  Ensure that you can use session manager to access the EC2 instance and that the instance can reach the internet.  The instance will also need a role that can write to CloudWatch.

Under the ec2-user home directory, install Python3 then create a venv environment.  Switch to the venv environment and upgrade pip.  Next, install the python packages flask, watchtower and waitress.

Create a target group using HTTP on port **5000**.  Create an Application Load Balancer listening on port 80 and routing to the target group.  Lastly, create a Cloudwatch agent log group called **cognito-learning** and a stream called **api**.

Fork this github repo to a new copy and switch to it.  Set up a deployment pipeline using your new github repo as the source, skip the build step and create a deployment to an EC2/On-prem instance.  The appspec.yml is already created and should work when the pipeline runs.

All things being equal, you should now have a python app runinng in a waitress container listening on port 5000.  The target group should update and the application load balancer become active.  Check that the /, /v1/public and /v1/secret uri's are all working.  The logs whould be goign to CloudWatch and the server.log in the ec2-user's home directory.

Next, set up DNS in Route 53 for your site.  Set up an SSL certificate for the site then create an https listener.  Set up http to forward to https on the ALB.  Set up Cognito to use a user pool and create application url redirects and logout url.  Edit the code in the app.py to take account of the new DNS name for your site.  Just search and replace the hostname part of any URL contained in the code.  Lastly, set up a new rule in the ALB to require authentication for /v1/secrets path, and use your newly created Cognito application as the target.  Forward the traffic to the target group if the logon is sucessful.

Now try the site again and this time you should see a logon page when you try to access the secrets page.  When loggedn in, you should see all the tokens in the CloudWatch logs.  You can grab them from there to decode them if you like or add more logging code to do that.

Next try the /logout link on the home page.  This will invoke the logout endpoint for Cognito as well as running the logout api on the server which invalidates the ALB cookies.  Check that the cookies have expired and that you are required to logon again should you see the /v1/secrets page.

Note that it is possible to invalidate the cookies using the /logout api call without first invoking the COgnito logout endpoint.  This doesn't really log you out and on the next run to the /v1/secrets page you will get a new cookie from the ALB!

# OAuth authentication flow

As per the diagram, you will observe 10 connections in the browser developer tools as you try to hit a page that requires authentication.

1. The user requests the url from the browser and the request makes it way to the load balancer.
2. The load balancer recognises a path that requires authentication and sends a redirect to the /oauth2/authorise endpoint that contains the client is, scope and state.
3. The browser then makes a request to the authorize endpoint.
4. The authorize endpoint gets the request and sends a redirect to the /login endpoint using all the information above.  The redirect_uri is the /idpresponse endpoint.
5. The broswer sends a request to the /login endpoint.
6. The login endpoint responds with the login page and a redirect_uri of the /idprespond endpoint.
7. The browser enters the user credentials in the logon page and posts it back to /login endpoint.
8. The /login endpoint authenticates the user, sets a Cognito cookie and then redirects the browser to the /idpresponse page.
9. The browser follows the redirect back to the /idpreponse endpoint along with the **code** which it must have got from the **/login** endpoint. which is the ALB, the ALB gets the Cognito cookie, and sends a 302 to the browser and sets the ALB cookie.
10. The Browser gets the cookie and follows the redirect to the resource.

When you refresh the secrets page the following steps happen:

1. Browser requests the resource with the ALB cookie.
2. ALB sends a redirect to the **/oauth2/authorise** endpoint.
3. The browser follows the redirect to the **authorise** endpoint, this time sending cookies Cognito, XSRF and congnito-fl.
4. The authorise endpoint responds with a redirect to the **/idpresponse** endpoint.
5. The browser follows the redirect to the **/idpresponse** endpoint with the ALB cookie and the **code** which it must have got from the **/oauth/authorize** endpoint.
6. The idpresponse endpoint sends a 302 to the resource and may also reset a new ALB cookie.
7. The broswer gets to the resource.