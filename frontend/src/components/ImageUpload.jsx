// src/components/ImageUpload.jsx
import React, { useState, useRef } from 'react';
import { FaCamera, FaCloudUploadAlt, FaTimes } from 'react-icons/fa';
import '../styles/ImageUpload.css';

const ImageUpload = ({ onAnalyzeImage, isLoading }) => {
  const [image, setImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && isValidImage(file)) {
      setImageFile(file);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);

    const file = event.dataTransfer.files[0];
    if (file && isValidImage(file)) {
      setImageFile(file);
    }
  };

  const setImageFile = (file) => {
    setImage(file);
    const fileReader = new FileReader();
    fileReader.onload = () => {
      setPreviewUrl(fileReader.result);
    };
    fileReader.readAsDataURL(file);
  };

  const clearImage = () => {
    setImage(null);
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const isValidImage = (file) => {
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
    return validTypes.includes(file.type);
  };

  const handleAnalyzeClick = () => {
    if (image && !isLoading) {
      onAnalyzeImage(image);
    }
  };

  return (
    <div className="image-upload-section card">
      <h2 className="section-title">
        <FaCamera className="section-icon" /> Upload Fridge Photo
      </h2>
      
      <div 
        className={`upload-area ${isDragging ? 'dragging' : ''} ${previewUrl ? 'has-image' : ''}`}
        onClick={() => fileInputRef.current.click()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input 
          type="file" 
          ref={fileInputRef}
          className="file-input" 
          accept="image/jpeg,image/png,image/jpg"
          onChange={handleFileSelect}
        />
        
        {previewUrl ? (
          <img src={previewUrl} alt="Preview" className="preview-image" />
        ) : (
          <div className="upload-placeholder">
            <FaCloudUploadAlt className="upload-icon" />
            <p className="upload-text">Drag & drop your image here or click to browse</p>
            <p className="upload-hint">Supports JPG, PNG files</p>
          </div>
        )}
      </div>
      
      <div className="upload-actions">
        <button 
          className="btn btn-primary analyze-btn"
          disabled={!image || isLoading}
          onClick={handleAnalyzeClick}
        >
          Analyze & Get Recipes
        </button>
        
        <button 
          className="btn btn-secondary clear-btn"
          onClick={clearImage}
          disabled={!image || isLoading}
        >
          <FaTimes /> Clear
        </button>
      </div>
    </div>
  );
};

export default ImageUpload;