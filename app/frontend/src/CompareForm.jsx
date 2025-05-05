import React, { useState } from 'react';
import FeedbackForm from './FeedbackForm';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function CompareForm({ selectedPose, uploadedImage, onResult }) {
  const [imageUrl, setImageUrl] = useState(null);
  const [score, setScore] = useState(null);
  const [guide, setGuide] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!selectedPose || !uploadedImage) {
      alert('Please select a pose and upload your image!');
      return;
    }
    setLoading(true);
    const formData = new FormData();
    formData.append('pose', selectedPose.id);
    formData.append('poseURL', selectedPose.url);
    formData.append('userImage', uploadedImage);

    try {
      await fetch(`${API_BASE_URL}/increment_popularity`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pose_id: selectedPose.id }),
      });
    } catch (error) {
      console.error('Failed to increment popularity:', error);
    }

    try {
      const response = await fetch(`${API_BASE_URL}/compare`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (response.ok){
        const imageUrl = `data:image/jpeg;base64,${data.image_base64}`;

        setImageUrl(imageUrl);
        setScore(data.score);
        setGuide(data.guide);
  
        onResult(selectedPose.id);
      }else{
        alert(`Oops! We couldn’t detect your pose in this photo. Please try uploading another one. Thanks a bunch!`);
      }
      
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (

    <div className="flex flex-col items-center mt-6 space-y-4">
      {loading && (
        <div className="flex items-center space-x-2 text-indigo-600 font-medium">
          <svg className="animate-spin h-6 w-6 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
          </svg>
          <span>Processing pose comparison...</span>
        </div>
      )}

      <button
        onClick={handleSubmit}
        className="bg-gradient-to-r from-indigo-500 to-purple-500 text-white py-3 px-8 rounded-full text-lg font-semibold shadow-lg hover:scale-105 transition-transform"
      >
        ✨ Get Pose Instructions
      </button>

      {imageUrl && (
        <div className="mt-6 text-center space-y-3">
          <img src={imageUrl} alt="Pose result" className="rounded-lg shadow-md max-w-md mx-auto" />
          <div className="text-lg text-gray-700">
            <p><strong>Score:</strong> {score}</p>
            <p><strong>Guide:</strong> {guide}</p>
          </div>
          <FeedbackForm
            poseId={selectedPose?.id}
            selectedPoseURL={selectedPose.url}
            uploadedImage={uploadedImage}
            resultImageUrl={imageUrl}
          />

        </div>

      )}
    </div>
  );
}

export default CompareForm;
