import urllib.request
import json
import os

repos = [
    "Hardware_Infernece_Engine_For_GPU",
    "Self_Improving_Agentic_System",
    "My_Kanha_Project",
    "wake_bot"
]

table = "| Project | Description | Link |\n|---|---|---|\n"

for repo in repos:
    url = f"https://api.github.com/repos/jhaabhijeet864/{repo}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            desc = data.get('description', 'No description available.')
            html_url = data.get('html_url')
            name = data.get('name')
            # Clean up description
            if desc:
                desc = desc.replace('\n', ' ').replace('\r', '').replace('|', '-')
            
            table += f"| 🚀 **[{name}]({html_url})** | {desc} | [View Repository]({html_url}) |\n"
    except Exception as e:
        print(f"Error fetching {repo}: {e}")
        table += f"| 🚀 **[{repo}](https://github.com/jhaabhijeet864/{repo})** | Open Source Project | [View Repository](https://github.com/jhaabhijeet864/{repo}) |\n"

print(table)
