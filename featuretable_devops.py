from haystack.dataclasses import ChatMessage
from google.ai.generativelanguage import FunctionDeclaration, Tool
from hbotrc import BotListener, BotCommands
import requests

# function Table
class DevOpTools:

    def __init__(self, username: str, token: str, base_url: str) -> None:
        self.auth = (username, token)
        self.base_url = base_url

    def start_build(self, jobname: str):
        url = f"{self.base_url}/job/{jobname}/build"
        response = requests.post(url, auth=self.auth)
        return {"status_code": response.status_code}

    def get_build_number(self, jobname: str):
        url = f"{self.base_url}/job/{jobname}/api/json"
        response = requests.get(url, auth=self.auth)
        build_number = response.json().get('lastBuild', {}).get('number', None)
        return {"build_number": build_number}

    def stop_build(self, jobname: str, build_number: int):
        b=int(build_number)
        url = f"{self.base_url}/job/{jobname}/{b}/stop"
        response = requests.post(url, auth=self.auth)
        return {"status_code": response.status_code}
    
    def get_all_jobs(self):
        url = f"{self.base_url}/api/json"
        response = requests.get(url, auth=self.auth)
        jobs = response.json().get('jobs', [])
        job_details = [{
            'name': job['name'],
            'status': job['color']
        } for job in jobs]
        return {"jobs": job_details}



    # Function Declarations
    start_build_func = FunctionDeclaration(
        name="start_build",
        description="Trigger a build on Jenkins for a specific job",
        parameters={
            "type_": "OBJECT",
            "properties": {
                "jobname": {"type_": "STRING", "description": "The name of the job to start"},
            },
            "required": ["jobname"],
        }
    )

    get_build_number_func = FunctionDeclaration(
        name="get_build_number",
        description="Retrieve the current build number from Jenkins for a specific job",
        parameters={
            "type_": "OBJECT",
            "properties": {
                "jobname": {"type_": "STRING", "description": "The name of the job to check"},
            },
            "required": ["jobname"],
        }
    )

    stop_build_func = FunctionDeclaration(
        name="stop_build",
        description="Stop a running build on Jenkins for a specific job",
        parameters={
            "type_": "OBJECT",
            "properties": {
                "jobname": {"type_": "STRING", "description": "The name of the job"},
                "build_number": {"type_": "INTEGER", "description": "The build number to stop"},
            },
            "required": ["jobname", "build_number"],
        }
    )

    get_all_jobs_func = FunctionDeclaration(
        name="get_all_jobs",
        description="Get , list  all job names from Jenkins along with the latest build status",
        parameters={
            "type_": "OBJECT",
            "properties": {},
            "required": [],
        }
    )


    def getFTable(self):
        return [
            self.start_build_func,
            self.get_build_number_func,
            self.stop_build_func,
            self.get_all_jobs_func
        ]

    # Function to invoke another function based on 'res' structure
    def dispatch(self,results):
        # Extract the necessary details from 'res'
        responses=[]

        for reply in results:
            function_name = reply.name
            parameters = reply.content

            # Check if the function exists in the global scope
            if function_name is not None:
                func = getattr(self, function_name, None)
                # Call the function with the unpacked parameters
                if callable(func):
                    print("callable! ")
                    result = func(**parameters)
                    responses.append(ChatMessage.from_function(content=result, name=function_name))
                else:
                    responses.append(ChatMessage.from_function(content=reply.content, name=None))

            else:
                responses.append(ChatMessage.from_function(content=reply.content, name=None))
                #raise NameError(f"Function is not defined.")
        return responses

    def getFTable(self):
         return [
            self.start_build_func,
            self.get_build_number_func,
            self.stop_build_func
        ]

    #end function TAble