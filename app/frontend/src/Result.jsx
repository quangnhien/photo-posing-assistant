import React from 'react';

function Result({ instructionImage }) {
  return (
    <div className="mt-8 text-center">
      <h2 className="text-2xl font-semibold mb-4">3️⃣ Follow These Instructions!</h2>
      <img src={instructionImage} alt="Pose Instruction" className="rounded-3xl mx-auto shadow-lg max-w-full h-auto" />
    </div>
  );
}

export default Result;
