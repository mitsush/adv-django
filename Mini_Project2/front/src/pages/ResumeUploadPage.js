import React, { useState } from 'react';
import { Upload, File, CheckCircle, XCircle } from 'lucide-react';
import Layout from '../components/Layout';

const ResumeUploadPage = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setUploadStatus(null);
    } else {
      setUploadStatus('error');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setUploading(true);
    
    // Simulate upload - replace with actual API call
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      setUploadStatus('success');
    } catch (error) {
      setUploadStatus('error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-3xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-gray-900">Upload Your Resume</h1>
          <p className="mt-2 text-gray-600">Upload your resume to apply for jobs faster</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <div 
            className={`border-2 border-dashed rounded-lg p-12 text-center ${
              file ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
            }`}
          >
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="hidden"
              id="resume-upload"
            />
            <label 
              htmlFor="resume-upload" 
              className="cursor-pointer flex flex-col items-center"
            >
              {file ? (
                <>
                  <File className="h-12 w-12 text-blue-500 mb-4" />
                  <p className="text-lg font-medium text-gray-900">{file.name}</p>
                  <p className="text-sm text-gray-500 mt-1">Click to change file</p>
                </>
              ) : (
                <>
                  <Upload className="h-12 w-12 text-gray-400 mb-4" />
                  <p className="text-lg font-medium text-gray-900">Drop your resume here</p>
                  <p className="text-sm text-gray-500 mt-1">or click to browse</p>
                  <p className="text-xs text-gray-400 mt-2">PDF files only, max 5MB</p>
                </>
              )}
            </label>
          </div>

          {uploadStatus === 'error' && (
            <div className="mt-4 flex items-center text-red-600">
              <XCircle className="h-5 w-5 mr-2" />
              <span>Please upload a valid PDF file</span>
            </div>
          )}

          {uploadStatus === 'success' && (
            <div className="mt-4 flex items-center text-green-600">
              <CheckCircle className="h-5 w-5 mr-2" />
              <span>Resume uploaded successfully!</span>
            </div>
          )}

          <button 
            onClick={handleUpload}
            disabled={!file || uploading}
            className={`mt-6 w-full py-3 px-4 rounded-lg font-medium text-white ${
              !file || uploading 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {uploading ? 'Uploading...' : 'Upload Resume'}
          </button>
        </div>
      </div>
    </Layout>
  );
};

export default ResumeUploadPage;