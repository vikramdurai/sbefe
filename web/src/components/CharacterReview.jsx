import React from 'react';

function CharacterReview({ formData }) {
    return (
        <div className="character-review">
            <h2>Review Your Character</h2>
            <p className="review-intro">
                Please review your answers before submitting. Your character sheet will be processed by the Sburb server.
            </p>

            <div className="review-section">
                <h3>Identity</h3>
                <dl>
                    <dt>Name:</dt><dd>{formData.identity.name || '(not provided)'}</dd>
                    <dt>Age:</dt><dd>{formData.identity.age}</dd>
                    <dt>Species:</dt><dd>{formData.identity.species}</dd>
                    <dt>Appearance:</dt><dd>{formData.identity.appearance || '(not provided)'}</dd>
                    <dt>Pronouns:</dt><dd>{formData.identity.pronouns || '(not provided)'}</dd>
                </dl>
            </div>

            <div className="review-section">
                <h3>Personality</h3>
                <dl>
                    <dt>Description:</dt><dd>{formData.personality.description || '(not provided)'}</dd>
                    <dt>Biggest Flaw:</dt><dd>{formData.personality.biggest_flaw || '(not provided)'}</dd>
                    <dt>Greatest Strength:</dt><dd>{formData.personality.greatest_strength || '(not provided)'}</dd>
                    <dt>Conflict Handling:</dt><dd>{formData.personality.conflict_handling || '(not provided)'}</dd>
                    <dt>Relationships:</dt><dd>{formData.personality.relationships || '(not provided)'}</dd>
                </dl>
            </div>

            <div className="review-section">
                <h3>Interests & Hobbies</h3>
                <dl>
                    <dt>Time Spent:</dt><dd>{formData.interests.time_spent || '(not provided)'}</dd>
                    <dt>Obsessions:</dt><dd>{formData.interests.obsessions || '(not provided)'}</dd>
                    <dt>Collections:</dt><dd>{formData.interests.collections || '(not provided)'}</dd>
                    <dt>Media:</dt><dd>{formData.interests.media || '(not provided)'}</dd>
                    <dt>Creations:</dt><dd>{formData.interests.creations || '(not provided)'}</dd>
                </dl>
            </div>

            <div className="review-section">
                <h3>Backstory</h3>
                <dl>
                    <dt>Life Story:</dt><dd>{formData.backstory.life_story || '(not provided)'}</dd>
                    <dt>Defining Event:</dt><dd>{formData.backstory.defining_event || '(not provided)'}</dd>
                    <dt>Guardian Relationship:</dt><dd>{formData.backstory.guardian_relationship || '(not provided)'}</dd>
                    <dt>Deepest Want:</dt><dd>{formData.backstory.deepest_want || '(not provided)'}</dd>
                </dl>
            </div>

            <div className="review-section">
                <h3>Final Questions</h3>
                <dl>
                    <dt>Sacrifice:</dt><dd>{formData.hidden_questions.sacrifice || '(not provided)'}</dd>
                    <dt>Expertise:</dt><dd>{formData.hidden_questions.expertise || '(not provided)'}</dd>
                    <dt>Reliance:</dt><dd>{formData.hidden_questions.reliance || '(not provided)'}</dd>
                    <dt>Time Perception:</dt><dd>{formData.hidden_questions.time_perception || '(not provided)'}</dd>
                    <dt>Hidden Depths:</dt><dd>{formData.hidden_questions.hidden_depths || '(not provided)'}</dd>
                    <dt>Problem Response:</dt><dd>{formData.hidden_questions.problem_response || '(not provided)'}</dd>
                </dl>
            </div>

            <div className="review-section">
                <h3>Session Setup</h3>
                <dl>
                    <dt>Multiplayer:</dt><dd>{formData.session.multiplayer ? 'Yes' : 'No'}</dd>
                    {formData.session.multiplayer && formData.session.player_names.length > 0 && (
                        <>
                            <dt>Players:</dt><dd>{formData.session.player_names.join(', ')}</dd>
                        </>
                    )}
                    <dt>Experience Type:</dt><dd>{formData.session.experience_type}</dd>
                    <dt>Permadeath:</dt><dd>{formData.session.permadeath}</dd>
                    {formData.session.content_flags && (
                        <>
                            <dt>Content to Avoid:</dt><dd>{formData.session.content_flags}</dd>
                        </>
                    )}
                </dl>
            </div>
        </div>
    );
}

export default CharacterReview;
