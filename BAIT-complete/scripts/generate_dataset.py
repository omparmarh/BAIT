import json
import random
import os

def generate_bait_instructions():
    scenarios = [
        {
            "category": "app_control",
            "templates": [
                "Open {app_name}, take a screenshot, and save it as {file_name}.",
                "Can you open {app_name} and then capture the screen?",
                "Launch {app_name} and screenshot the current view to {file_name}.",
            ],
            "apps": ["Safari", "Chrome", "Notes", "Spotify", "TextEdit", "Terminal", "Finder"],
            "responses": [
                "Thinking: I need to open the app first, then use the screenshot tool. Action: open_app('{app_name}') -> screenshot('{file_name}') -> Done. Summary: I've opened {app_name} and saved the screenshot as {file_name}.",
                "Thought: Launching {app_name}... Screenshotting... Observation: Done. I have opened {app_name} and captured the screen to {file_name}."
            ]
        },
        {
            "category": "web_research",
            "templates": [
                "Research {topic} and summarize it in a new file called {file_name}.",
                "Search the web for {topic}, then create a note {file_name} with the findings.",
                "Find information about {topic} online and write a summary to {file_name}."
            ],
            "topics": ["latest AI trends", "M1 Mac performance", "Python FastAPI best practices", "Gujarat tourism", "stock market today"],
            "responses": [
                "Thinking: I should search the web for {topic} first, then write the results to a file. Action: web_search('{topic}') -> create_file('{file_name}', content) -> Done. Summary: I researched {topic} and saved the summary to {file_name}.",
            ]
        },
        {
            "category": "file_ops",
            "templates": [
                "Create a python script named {file_name} that {logic}.",
                "Write a file {file_name} containing {content}.",
                "Edit {file_name} to include {new_info}."
            ],
            "logics": ["calculates fibonacci sequence", "scrapes a website", "manages a todo list"],
            "contents": ["a list of recipes", "my meeting notes", "a shopping list"],
            "responses": [
                "Thinking: I will generate the code and save it to {file_name}. Action: create_file('{file_name}', code) -> Done. Summary: I've created the script {file_name} with the requested logic.",
            ]
        }
    ]

    dataset = []
    
    # Generate ~10k items by mixing and matching
    for _ in range(10000):
        scenario = random.choice(scenarios)
        template = random.choice(scenario["templates"])
        
        # Fill placeholders
        app_name = random.choice(scenario.get("apps", ["App"]))
        file_name = f"{random.randint(100, 999)}_{random.choice(['notes', 'data', 'output', 'results'])}.txt"
        topic = random.choice(scenario.get("topics", ["AI"]))
        logic = random.choice(scenario.get("logics", ["dosth"]))
        content = random.choice(scenario.get("contents", ["some text"]))
        new_info = "more data"
        
        instruction = template.format(
            app_name=app_name, 
            file_name=file_name, 
            topic=topic, 
            logic=logic, 
            content=content,
            new_info=new_info
        )
        
        response_template = random.choice(scenario["responses"])
        response = response_template.format(
            app_name=app_name, 
            file_name=file_name, 
            topic=topic,
            logic=logic
        )
        
        dataset.append({
            "instruction": instruction,
            "input": "",
            "output": response
        })

    os.makedirs("datasets", exist_ok=True)
    with open("datasets/bait_instructions.jsonl", "w") as f:
        for entry in dataset:
            f.write(json.dumps(entry) + "\n")
    
    print(f"Generated {len(dataset)} instructions in datasets/bait_instructions.jsonl")

if __name__ == "__main__":
    generate_bait_instructions()
