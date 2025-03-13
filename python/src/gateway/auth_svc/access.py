import os, requests

def login(request):
    auth = request.authorization
    if not auth:
        return None, ("missing credentials", 401)

    # Get basic auth from auth object
    basic_auth = (auth.username, auth.password)

    # Make a post request to our auth service
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login",
        auth = basic_auth
    )

    if response.status_code == 200:
        return response.txt, None
    else:
        return None, (response.txt, response.status_code)