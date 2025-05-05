import React, { useState } from 'react';

function FeedbackForm({ poseId }) {
  const [useful, setUseful] = useState(null); // true / false
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async () => {
    if (useful === null) return;
  
    const formData = new FormData();
    formData.append('pose_id', poseId);
    formData.append('is_useful', useful);
    formData.append('comment', comment.trim());
    formData.append('pose_data', JSON.stringify(selectedPose));
    formData.append('image_url', resultImageUrl);
    formData.append('uploaded_image', uploadedImage); // actual image file
  
    try {
      const response = await fetch(`${API_BASE_URL}/submit_feedback`, {
        method: 'POST',
        body: formData,
      });
  
      if (response.ok) {
        setSubmitted(true);
      } else {
        alert('❌ Failed to submit feedback.');
      }
    } catch (err) {
      console.error(err);
      alert('❌ Error submitting feedback.');
    }
  };
  

  return (
    <div className="mt-6 text-center">
      {submitted ? (
        <p className="text-green-600 font-medium">✅ Thank you for your feedback!</p>
      ) : (
        <>
          <h3 className="text-lg font-semibold mb-4 text-gray-700">Was this result helpful?</h3>
          <div className="flex justify-center gap-4 mb-4">
            <button
              onClick={() => setUseful(true)}
              className={`px-4 py-2 rounded-full font-semibold border ${
                useful === true ? 'bg-green-500 text-white' : 'bg-white text-green-600 border-green-500'
              }`}
            >
              👍 Yes
            </button>
            <button
              onClick={() => setUseful(false)}
              className={`px-4 py-2 rounded-full font-semibold border ${
                useful === false ? 'bg-red-500 text-white' : 'bg-white text-red-600 border-red-500'
              }`}
            >
              👎 No
            </button>
          </div>

          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            className="w-full max-w-md mx-auto p-2 border rounded-md resize-none mb-4"
            rows={3}
            placeholder="Optional: Tell us why..."
          />

          <br />
          <button
            onClick={handleSubmit}
            className="px-4 py-2 bg-indigo-500 text-white rounded-full font-semibold"
            disabled={useful === null}
          >
            Submit Feedback
          </button>
        </>
      )}
    </div>
  );
}

export default FeedbackForm;
