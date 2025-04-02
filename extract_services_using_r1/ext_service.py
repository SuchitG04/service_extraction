import os
import json
import openai
import requests
import time
from dotenv import load_dotenv
from multiprocessing import Process, Queue

load_dotenv()

OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_BASE
)

instructions = """\
Instructions:
- In the given code file, identify all services acting as data sinks. A data sink is defined as any service/component that receives and stores/transmits data from the application. Focus on extracting the **service name** as used in the code, not the underlying sink's or product's name (e.g., instead of "database", look for the specific service/component name like "userDBService").
- A service can be a database, API, external system, logging service, file system, etc.
- Output the name of the service that's acting as a data sink.

Note: Focus on extracting the service name as it appears in the code (e.g., "loggingService", "fileStorage", etc.), AND NOT the underlying sink's name (e.g., "Redis", "RabbitMQ", "Upstash", "AWS S3 Object Storage", "PostgreSQL Database", etc.).

---

JSON Output Format:

{{
    "detected_data_sink_services": [
        {{
            "service": "[short and relevant service/component name]",
            "evidence": "[the exact code snippet showing the sink operation]",
            "reasoning": "[explanation of why this is a data sink]"
        }},
        {{
            "service": "[short and relevant service/component name]",
            "evidence": "[the exact code snippet showing the sink operation]",
            "reasoning": "[explanation of why this is a data sink]"
        }},
        ...
    ]
}}

---

Example:

If the code contains:

```typescript
export const seedUserWorkspaces = async (
  workspaceDataSource: DataSource,
  schemaName: string,
  workspaceId: string,
) => {{
  await workspaceDataSource
    .createQueryBuilder()
    .insert()
    .into(`${{schemaName}}.${{tableName}}`, ['id', 'userId', 'workspaceId'])
    .orIgnore()
    .values([
      {{
        id: DEV_SEED_USER_WORKSPACE_IDS.NOAH,
        userId: DEMO_SEED_USER_IDS.NOAH,
        workspaceId: workspaceId,
      }},
      {{
        id: DEV_SEED_USER_WORKSPACE_IDS.HUGO,
        userId: DEMO_SEED_USER_IDS.HUGO,
        workspaceId: workspaceId,
      }},
      {{
        id: DEV_SEED_USER_WORKSPACE_IDS.TIM,
        userId: DEMO_SEED_USER_IDS.TIM,
        workspaceId: workspaceId,
      }},
    ])
    .execute();
}};

export const deleteUserWorkspaces = async (
  workspaceDataSource: DataSource,
  schemaName: string,
  workspaceId: string,
) => {{
  await workspaceDataSource
    .createQueryBuilder()
    .delete()
    .from(`${{schemaName}}.${{tableName}}`)
    .where(`"${{tableName}}"."workspaceId" = :workspaceId`, {{
      workspaceId,
    }})
    .execute();
}};
```

The output should be:

{{
    "detected_data_sink_services": [
        {{
            "service": "workspaceDataSource",
            "evidence": "await workspaceDataSource\n    .createQueryBuilder()\n    .insert()\n    .into(`${{schemaName}}.${{tableName}}`, ['id', 'userId', 'workspaceId'])\n    .orIgnore()\n    .values([\n      {{\n        id: DEV_SEED_USER_WORKSPACE_IDS.NOAH,\n        userId: DEMO_SEED_USER_IDS.NOAH,\n        workspaceId: workspaceId,\n      }},\n      {{\n        id: DEV_SEED_USER_WORKSPACE_IDS.HUGO,\n        userId: DEMO_SEED_USER_IDS.HUGO,\n        workspaceId: workspaceId,\n      }},\n      {{\n        id: DEV_SEED_USER_WORKSPACE_IDS.TIM,\n        userId: DEMO_SEED_USER_IDS.TIM,\n        workspaceId: workspaceId,\n      }},\n    ])\n    .execute();",
            "reasoning": "The service 'workspaceDataSource' is used to insert data into a table, indicating it is acting as a data sink."
        }},
        {{
            "service": "workspaceDataSource",
            "evidence": "await workspaceDataSource\n    .createQueryBuilder()\n    .delete()\n    .from(`${{schemaName}}.${{tableName}}`)\n    .where(`\"${{tableName}}\".\"workspaceId\" = :workspaceId`, {{\n      workspaceId,\n    }})\n    .execute();",
            "reasoning": "The service 'workspaceDataSource' is used to delete data from a table, indicating it is acting as a data sink."
        }}
    ]
}}

---

File path:
{file_path}

---

File content:
```
{file_content}
```
"""


def get_completions(context_to_send, queue):
    url = "https://api.fireworks.ai/inference/v1/chat/completions"
    payload = {
        "model": "accounts/fireworks/models/deepseek-r1",
        "max_tokens": 32768,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "response_format": {
            "type": "json_object"
        },
        "messages": [
            {
                "role": "user",
                "content": context_to_send
            }
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }
    response = requests.post(url, json=payload, headers=headers)
    result = response.json()['choices'][0]['message']['content']
    queue.put(result)


def main():
    responses = []
    file_info = json.load(open('sink_files.json', 'r'))
    batch_sz = 10
    
    i = 0
    file_not_found_count = 0
    files_not_found = []
    for batch_idx in range(0, len(file_info), batch_sz):
        print(f"Processing batch {i+1}")
        batch = file_info[batch_idx:batch_idx+batch_sz]
        processes = []
        queues = []
        start_time = time.time()
        # Start processes for the batch
        for file_name in batch:
            try:
                with open(f"/home/suchitg/DataCare/{file_name['filename']}", 'r') as f:
                    file_content = f.read()
            except FileNotFoundError:
                file_not_found_count += 1
                files_not_found.append(file_name['filename'])
                continue

            queue = Queue()
            process = Process(target=get_completions, args=(instructions.format(file_path=file_name['filename'], file_content=file_content), queue))
            process.start()
            processes.append(process)
            queues.append((file_name, queue))
        
        # Collect results from this batch
        for process, (file_name, queue) in zip(processes, queues):
            response = queue.get()  # blocks until result is available
            reasoning, message = response.split("</think>")
            responses.append({
                "filename": file_name['filename'],
                "message": json.loads(message.strip()),
                "reasoning": reasoning.replace("<think>", "").strip()
            })
            process.join() 
        
        end_time = time.time()
        print(f"Batch {i+1} processed in {end_time - start_time:.2f} seconds")
        print("-"*20)
        i += 1
            
    json.dump(responses, open('service_extraction.json', 'w'), indent=4)
    print("Saved service extraction results to service_extraction.json")
    print(f"{file_not_found_count} files not found")
    print(f"Files not found: {files_not_found}")

if __name__ == "__main__":
    main()