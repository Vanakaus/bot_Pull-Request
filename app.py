import os
from flask import Flask, request
from github import Github, GithubIntegration

app = Flask(__name__)

app_id = '187088'

# Read the bot certificate
with open(
        os.path.normpath(os.path.expanduser('bot_key.pem')),
        'r'
) as cert_file:
    app_key = cert_file.read()
    
# Create an GitHub integration instance
git_integration = GithubIntegration(
    app_id,
    app_key,
)

def pr_merged_event(repo, payload):
    pr = repo.get_issue(number=payload['pull_request']['number'])
    author = pr.user.login

    response = f"Thanks for opening this pull request, @{author}! " \
               f"The repository maintainers will look into it ASAP! :speech_balloon:"
    pr.create_comment(f"{response}")
    branch = payload['pull_request']['head']['ref']
    repo.get_git_ref(f"heads/{branch}").delete()

@app.route("/", methods=['POST'])
def bot():
    payload = request.json

    if not 'repository' in payload.keys():
        return "", 204

    owner = payload['repository']['owner']['login']
    repo_name = payload['repository']['name']

    git_connection = Github(
        login_or_token=git_integration.get_access_token(
            git_integration.get_installation(owner, repo_name).id
        ).token
    )
    repo = git_connection.get_repo(f"{owner}/{repo_name}")

    # Check if the event is a GitHub pull request merged event
    if all(k in payload.keys() for k in ['action', 'pull_request']) and payload['action'] == 'closed':
        merged = payload['pull_request']['merged']
        if merged:
            pr_merged_event(repo, payload)

    return "", 204

if __name__ == "__main__":
    app.run(debug=True, port=5000)
