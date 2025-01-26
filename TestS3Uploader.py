import unittest
from unittest.mock import Mock, patch
import boto3
import os
import json
from botocore.exceptions import ClientError
from s3Connect import S3Uploader  # Assumes the original class is in s3_uploader.py

class TestS3Uploader(unittest.TestCase):
    def setUp(self):
        # Setup common test parameters
        self.bucket_name = 'podcast.monitor'
        self.prefix = 'test-prefix/'
        self.uploader = S3Uploader(self.bucket_name, self.prefix)

    def test_init(self):
        # Test initialization
        self.assertEqual(self.uploader.bucket_name, self.bucket_name)
        self.assertEqual(self.uploader.prefix, 'test-prefix/')

        # Test prefix handling
        uploader_no_prefix = S3Uploader(self.bucket_name)
        self.assertEqual(uploader_no_prefix.prefix, '')

    def test_get_full_key(self):
        # Test key combination with prefix
        self.assertEqual(
            self.uploader._get_full_key('test-file.txt'), 
            'test-prefix/test-file.txt'
        )
        
        # Test key with leading slash
        self.assertEqual(
            self.uploader._get_full_key('/test-file.txt'), 
            'test-prefix/test-file.txt'
        )

    @patch('boto3.client')
    def test_upload_string(self, mock_boto3_client):
        # Mock S3 client
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client

        # Test successful upload
        result = self.uploader.upload_string('test content', 'test.txt')
        self.assertTrue(result)
        mock_s3_client.put_object.assert_called_once_with(
            Bucket=self.bucket_name,
            Key='test-prefix/test.txt',
            Body='test content'
        )

        # Test upload failure
        mock_s3_client.put_object.side_effect = ClientError({}, 'PutObject')
        result = self.uploader.upload_string('test content', 'test.txt')
        self.assertFalse(result)

    @patch('boto3.client')
    def test_upload_file(self, mock_boto3_client):
        # Mock S3 client and os.path
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client

        with patch('os.path.basename', return_value='test.txt'):
            # Test successful upload with default key
            result = self.uploader.upload_file('to_be_processed.json')
            self.assertTrue(result)
            mock_s3_client.upload_file.assert_called_once_with(
                Filename='to_be_processed.txt',
                Bucket=self.bucket_name,
                Key='test-prefix/test.txt'
            )

        # Test upload with custom key
        result = self.uploader.upload_file('/path/to/test.txt', 'custom/path.txt')
        self.assertTrue(result)
        mock_s3_client.upload_file.assert_called_with(
            Filename='/path/to/test.txt',
            Bucket=self.bucket_name,
            Key='test-prefix/custom/path.txt'
        )

    @patch('boto3.client')
    def test_upload_json(self, mock_boto3_client):
        # Mock S3 client
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client

        # Test JSON upload
        test_data = {"key": "value"}
        result = self.uploader.upload_json(test_data, 'data.json')
        self.assertTrue(result)
        mock_s3_client.put_object.assert_called_once_with(
            Bucket=self.bucket_name,
            Key='test-prefix/data.json',
            Body=json.dumps(test_data),
            ContentType='application/json'
        )

    @patch('os.walk')
    @patch('boto3.client')
    def test_upload_folder(self, mock_boto3_client, mock_walk):
        # Mock S3 client and os.walk
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client

        # Simulate folder structure
        mock_walk.return_value = [
            ('/path/to/folder', [], ['file1.txt', 'file2.txt']),
            ('/path/to/folder/subfolder', [], ['file3.txt'])
        ]

        with patch('os.path.exists', return_value=True), \
             patch('os.path.relpath', side_effect=['file1.txt', 'file2.txt', 'subfolder/file3.txt']), \
             patch.object(S3Uploader, 'upload_file', return_value=True) as mock_upload:
            
            # Test folder upload
            results = self.uploader.upload_folder('/path/to/folder')
            
            # Verify upload calls
            self.assertEqual(mock_upload.call_count, 3)
            self.assertEqual(results['success'], 3)
            self.assertEqual(results['failed'], 0)

    @patch('boto3.client')
    def test_read_s3_file(self, mock_boto3_client):
        # Mock S3 client and response
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client

        # Test text file reading
        mock_s3_client.get_object.return_value = {
            'Body': Mock(read=lambda: b'test content')
        }
        result = self.uploader.read_s3_file('test.txt')
        self.assertEqual(result, 'test content')

        # Test JSON file reading
        mock_s3_client.get_object.return_value = {
            'Body': Mock(read=lambda: b'{"key": "value"}')
        }
        result = self.uploader.read_s3_file('test.json', file_type='json')
        self.assertEqual(result, {"key": "value"})

        # Test unsupported file type
        with self.assertRaises(ValueError):
            self.uploader.read_s3_file('test.txt', file_type='unsupported')

    def test_list_files_by_bucket(self):
        # Mock paginator and S3 client
        mock_paginator = Mock()
        mock_pages = [
            {
                'Contents': [
                    {
                        'Key': 'folder/file1.txt', 
                        'Size': 100, 
                        'LastModified': 'timestamp',
                        'Name': 'file1.txt'
                    },
                    {
                        'Key': 'folder/file2.txt', 
                        'Size': 200, 
                        'LastModified': 'timestamp',
                        'Name': 'file2.txt'
                    }
                ]
            }
        ]
        mock_paginator.paginate.return_value = mock_pages

        with patch.object(self.uploader.s3_client, 'get_paginator', return_value=mock_paginator):
            result = self.uploader.list_files_by_bucket(self.bucket_name, 'folder/')
            
            # Verify results
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['name'], 'file1.txt')

if __name__ == '__main__':
    unittest.main()