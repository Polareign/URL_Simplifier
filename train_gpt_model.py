import openai
import time
import json

openai.api_key = "KEY"

def upload_training_file(file_path):
    with open(file_path, "rb") as f:
        response = openai.files.create(
            file=f,
            purpose="fine-tune"
        )
    return response.id

def create_fine_tuning_job(file_id, model="gpt-3.5-turbo"):
    response = openai.fine_tuning.jobs.create(
        training_file=file_id,
        model=model
    )
    return response.id

def check_fine_tuning_status(job_id):
    while True:
        response = openai.fine_tuning.jobs.retrieve(job_id)
        status = response.status
        print(f"Fine-tuning status: {status}")
        if status in ["succeeded", "failed", "cancelled"]:
            return response 
        time.sleep(30)

def get_fine_tuned_model(job_id):
    response = openai.fine_tuning.jobs.retrieve(job_id) 
    if response.status == "succeeded":
        return response.fine_tuned_model
    return None

def main():
    training_file = "training_data.jsonl"
    print("Uploading training file...")
    file_id = upload_training_file(training_file)
    print(f"File uploaded: {file_id}")
    
    print("Starting fine-tuning job...")
    job_id = create_fine_tuning_job(file_id)
    print(f"Fine-tuning job created: {job_id}")
    
    print("Monitoring fine-tuning process...")
    final_status = check_fine_tuning_status(job_id)
    
    if final_status.status == "succeeded":
        fine_tuned_model = get_fine_tuned_model(job_id)
        print(f"Fine-tuned model ID: {fine_tuned_model}")
    else:
        print("Fine-tuning failed.")

job_id = "ftjob-bY42r2QIFTF8e0UD2BPI3gyV"  # Replace with your actual job ID
response = openai.fine_tuning.jobs.retrieve(job_id)
print(response)

if __name__ == "__main__":
    main()