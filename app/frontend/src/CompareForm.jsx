import React from 'react';

function CompareForm({ selectedPose, uploadedImage, onResult }) {
  const handleSubmit = async () => {
    if (!selectedPose || !uploadedImage) {
      alert('Please select a pose and upload your image!');
      return;
    }

    const formData = new FormData();
    formData.append('pose', selectedPose.id);
    formData.append('userImage', uploadedImage);

    const response = await fetch('/api/compare', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    onResult(data.instructionImageUrl);
  };

  return (
    <div className="flex justify-center mt-6">
      <button 
        onClick={handleSubmit}
        className="bg-gradient-to-r from-indigo-500 to-purple-500 text-white py-3 px-8 rounded-full text-lg font-semibold shadow-lg hover:scale-105 transition-transform"
      >
        ✨ Get Pose Instructions
      </button>
    </div>
  );
}

export default CompareForm;
