import React, { useState } from 'react';
import FeedbackForm from './FeedbackForm';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function CompareForm({ selectedPose, uploadedImage, onResult }) {
  const [imageUrl, setImageUrl] = useState(null);
  const [score, setScore] = useState(null);
  const [guide, setGuide] = useState('');

  const handleSubmit = async () => {
    if (!selectedPose || !uploadedImage) {
      alert('Please select a pose and upload your image!');
      return;
    }

    const formData = new FormData();
    formData.append('pose', selectedPose.id);
    console.log(selectedPose.url)
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
      const imageUrl = `data:image/jpeg;base64,${data.image_base64}`;

      setImageUrl(imageUrl);
      setScore(data.score);
      setGuide(data.guide);

      onResult(selectedPose.id);
    } catch (error) {
      console.error('Comparison failed:', error);
    }
  };

  return (
    <div className="flex flex-col items-center mt-6 space-y-4">
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
          <FeedbackForm poseId={selectedPose?.id} />
        </div>
        
      )}
    </div>
  );
}

export default CompareForm;
