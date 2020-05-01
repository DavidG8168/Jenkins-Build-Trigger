# *************************************************************
# Jenkins related imports & utility.
import requests
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.crumb_requester import CrumbRequester
from time import sleep

# *************************************************************
# Jenkins details.
# Jenkins login username.
usr_name = 'YOUR_USERNAME'
# Jenkins login password.
usr_pass = 'YOUR_PASSWORD'
# Authorization header.
usr_auth = "{0}:{1}@".format(usr_name, usr_pass)
# Jenkins url (Example: 'http://localhost:8080').
usr_url = 'YOUR_JENKINS_URL'
# Jenkins jobs to trigger builds of (Example: ['job1', 'job2', 'job3']).
usr_job_names = ['JENKINS_JOB_TO_BUILD']


# *************************************************************
# Create Jenkins object.
def create_jenkins():
    jenkins = Jenkins(
        usr_url, username=usr_name, password=usr_pass,
        requester=CrumbRequester(
            baseurl=usr_url,
            username=usr_name,
            password=usr_pass
        )
    )
    return jenkins


# *************************************************************
# Trigger each job build in the list with no wait.
def parallel_trigger(jenkins):
    for job in usr_job_names:
        jenkins.jobs.build(job)


# *************************************************************
# Trigger each job build in the list while waiting for previous to finish beforehand.
# Also prints latest build console output.
def sequential_trigger(jenkins):
    for job in usr_job_names:
        trigger_job = jenkins.create_job(job, None)
        queue = trigger_job.invoke()
        queue.block_until_complete()
        print(get_job_console_output(job))


# *************************************************************
# Create path to last console output.
def get_job_console_output(job_name):
    # Path of job.
    job_path = "{0}/{1}".format("job", job_name)
    # Path of the job's latest console output.
    console_path = "{0}{1}".format(job_path, "/lastBuild/consoleText")
    # Sleep to avoid too many HTTP requests exception.
    try:
        sleep(2)
        # Authenticate to get the console output using HTTP request.
        console_url = "{0}/{1}".format(usr_url, console_path)
        # Insert username:pass@ to request after http://.
        auth_url = add_authorization(console_url, "http://", usr_auth)
        return requests.get("{0}/{1}".format(auth_url, console_path), verify=False).text
    except requests.exceptions.ConnectionError:
        return None


# *************************************************************
# Adds authorization, username:password to request url.
def add_authorization(source, target, token):
    index = source.find(target)
    return source[:index + len(target)] + token + source[index + len(target):]


# *************************************************************
# Run example.
if __name__ == '__main__':
    # Create the instance.
    jenkins_instace = create_jenkins()
    # Trigger all builds in list.
    parallel_trigger(jenkins_instace)
    # Trigger builds one by one while printing console output after build.
    sequential_trigger(jenkins_instace)
