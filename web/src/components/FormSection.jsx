import React from 'react';

function FormSection({ title, description, children }) {
    return (
        <div className="form-section">
            <h2>{title}</h2>
            {description && <p className="section-description">{description}</p>}
            <div className="section-fields">
                {children}
            </div>
        </div>
    );
}

export default FormSection;
