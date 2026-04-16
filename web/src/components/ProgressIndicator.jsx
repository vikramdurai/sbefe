import React from 'react';

function ProgressIndicator({ currentStep, totalSteps }) {
    const percentage = (currentStep / totalSteps) * 100;

    return (
        <div className="progress-indicator">
            <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${percentage}%` }}></div>
            </div>
            <div className="progress-text">
                Section {currentStep} of {totalSteps}
            </div>
        </div>
    );
}

export default ProgressIndicator;
