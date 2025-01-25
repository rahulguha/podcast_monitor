import boto3
import json
from botocore.exceptions import ClientError
import os
from pathlib import Path
from datetime import date, datetime
from typing import List, Dict, Optional 

class S3Uploader:
    def __init__(self, bucket_name: str, prefix: str = ""):
        """
        Initialize S3 uploader with bucket name and optional prefix
        
        Args:
            bucket_name (str): The S3 bucket name
            prefix (str): Optional prefix for all uploads (like a folder path)
        """
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name
        # Remove leading/trailing slashes and ensure trailing slash if prefix exists
        self.prefix = prefix.strip('/') + '/' if prefix else ''



    def _get_full_key(self, key: str) -> str:
        """Combine prefix with key, ensuring clean path format"""
        # Remove leading slash from key to avoid double slashes
        key = key.lstrip('/')
        return f"{self.prefix}{key}"

    def list_files_by_bucket(self, bucket_name, prefix, suffix: str=None, max_files: int=None) ->list:
        try:
            prefix = prefix.strip('/')
            if prefix and not prefix.endswith('/'):
                prefix += '/'
            params = {
                'Bucket': bucket_name,
                'Prefix': prefix
            }
            # print(params)
            files = []
            paginator = self.s3_client.get_paginator('list_objects_v2')
        
            for page in paginator.paginate(**params):
                if 'Contents' not in page:
                    continue
                    
                for obj in page['Contents']:
                    # Skip if it's a folder (ends with '/')
                    if obj['Key'].endswith('/'):
                        continue
                        
                    # Apply suffix filter if specified
                    if suffix and not obj['Key'].lower().endswith(suffix.lower()):
                        continue
                    
                    file_info = {
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'name': obj['Key'].split('/')[-1]
                    }
                    
                    files.append(file_info)
                    
                    # Check if we've reached max_files
                    if max_files and len(files) >= max_files:
                        return files
                return files
        except ClientError as e:
            print(f"Error listing files: {e}")
            return []
        

    def upload_string(self, content: str, key: str) -> bool:
        """Upload a string to S3 with prefix"""
        try:
            
            full_key = self._get_full_key(key)
            # print (full_key)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=full_key,
                Body=content
            )
            print(f"Successfully uploaded to s3://{self.bucket_name}/{full_key}")
            return True
        except ClientError as e:
            print(f"Error uploading string to S3: {e}")
            return False

    def upload_file(self, file_path: str, key: str = None) -> bool:
        """Upload a file to S3 with prefix"""
        try:
            # If no key is provided, use the filename
            if key is None:
                key = os.path.basename(file_path)
            
            full_key = self._get_full_key(key)
            self.s3_client.upload_file(
                Filename=file_path,
                Bucket=self.bucket_name,
                Key=full_key
            )
            print(f"Successfully uploaded to s3://{self.bucket_name}/{full_key}")
            return True
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return False

    def upload_json(self, data: dict, key: str) -> bool:
        """Upload JSON data to S3 with prefix"""
        try:
            full_key = self._get_full_key(key)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=full_key,
                Body=json.dumps(data),
                ContentType='application/json'
            )
            print(f"Successfully uploaded to s3://{self.bucket_name}/{full_key}")
            return True
        except ClientError as e:
            print(f"Error uploading JSON to S3: {e}")
            return False

    def upload_folder(self, local_folder: str, subfolder: str = "") -> dict:
        """
        Upload an entire folder to S3 with prefix
        
        Args:
            local_folder (str): Path to local folder
            subfolder (str): Optional additional subfolder within the prefix
        """
        results = {"success": 0, "failed": 0, "errors": []}
        
        try:
            folder_path = Path(local_folder)
            if not folder_path.exists():
                raise ValueError(f"Folder not found: {local_folder}")

            for root, _, files in os.walk(folder_path):
                for file in files:
                    local_path = os.path.join(root, file)
                    # Calculate relative path from the base folder
                    relative_path = os.path.relpath(local_path, local_folder)
                    
                    # Combine subfolder with relative path
                    if subfolder:
                        s3_key = os.path.join(subfolder, relative_path)
                    else:
                        s3_key = relative_path

                    if self.upload_file(local_path, s3_key):
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Failed to upload: {relative_path}")

        except Exception as e:
            results["failed"] += 1
            results["errors"].append(str(e))

        return results

    
    
    def read_s3_file(self,  key: str, file_type: str = 'text'):
        """
        Read a file from S3 bucket
        
        Args:
            bucket_name (str): Name of the S3 bucket
            key (str): Path to the file in S3
            file_type (str): Type of file to read ('text', 'json', 'csv', 'binary')
        
        Returns:
            The file contents in the appropriate format
        """
        try:
            
            
            # Get the object from S3
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            # Read the file contents based on type
            if file_type == 'text':
                # Read as text
                return response['Body'].read().decode('utf-8')
                
            elif file_type == 'json':
                # Parse JSON content
                return json.loads(response['Body'].read().decode('utf-8'))
                
            elif file_type == 'csv':
                # Read as pandas DataFrame
                return pd.read_csv(response['Body'])
                
            elif file_type == 'binary':
                # Return raw bytes
                return response['Body'].read()
                
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
        except ClientError as e:
            print(f"Error reading file from S3: {e}")
            return None

    def list_s3_folders1(bucket_name, prefix='', debug=True):
        s3_client = boto3.client('s3')
    
        # Remove leading slash from prefix
        prefix = prefix.lstrip('/')
        
        try:
            # List objects directly
            response = s3_client.list_objects_v2(
                Bucket=bucket_name, 
                Prefix=prefix,
                Delimiter='/'
            )
            
            # Extract folders and objects
            folders = [
                obj['Prefix'] for obj in response.get('CommonPrefixes', [])
            ]
            
            # If no folders, list all objects under prefix
            if not folders:
                objects = [
                    obj['Key'] for obj in response.get('Contents', [])
                    if obj['Key'] != prefix
                ]
                return objects
            
            return folders
        
        except Exception as e:
            print(f"Error: {e}")
            return []


    def list_s3_folders(bucket_name, prefix=''):
        # s3 = boto3.client('s3')
        s3 = boto3.resource('s3')

        # List objects with the specified prefix
        # paginator = s3.get_paginator('list_objects_v2')
        folders = set()
        bucket = s3.Bucket(bucket_name)
        for obj in bucket.objects.filter(Prefix=prefix, Delimiter='/'):
            if obj.key != prefix:
                folders.add(obj.key)
        return list(folders)
# Example usage
if __name__ == "__main__":
    now = datetime.now()
    formatted_date = now.strftime("%m-%d-%y")
    # Initialize uploader with bucket and prefix
    uploader = S3Uploader(
        bucket_name="podcast.monitor",
        prefix=f"transcription/{formatted_date}"  # All files will be uploaded under this prefix
    )
    
    # Example 1: Upload a string
    uploader.upload_string(
        content="Hello, S3!",
        key="hello2.txt"  # Will be uploaded as "data/2024/hello.txt"
    )
    
    # # Example 2: Upload a file
    # uploader.upload_file(
    #     file_path="local_file.pdf",
    #     key="documents/file.pdf"  # Will be uploaded as "data/2024/documents/file.pdf"
    # )
    
    # # Example 3: Upload JSON
    # sample_data = {"name": "John", "age": 30}
    # uploader.upload_json(
    #     data=sample_data,
    #     key="users/john.json"  # Will be uploaded as "data/2024/users/john.json"
    # )
    
    # # Example 4: Upload entire folder
    # results = uploader.upload_folder(
    #     local_folder="./my_local_folder",
    #     subfolder="backup"  # Will be uploaded under "data/2024/backup/"
    # )
    
    # # Print folder upload results
    # print("\nFolder Upload Summary:")
    # print(f"Successfully uploaded: {results['success']} files")
    # print(f"Failed uploads: {results['failed']}")
    # if results["errors"]:
    #     print("\nErrors:")
    #     for error in results["errors"]:
    #         print(f"- {error}")