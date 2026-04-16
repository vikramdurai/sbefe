import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FormSection from '../components/FormSection';
import ProgressIndicator from '../components/ProgressIndicator';
import CharacterReview from '../components/CharacterReview';

const TOTAL_STEPS = 7; // 6 sections + 1 review
const DRAFT_KEY = 'sburb_character_draft';

function CharacterCreator() {
    const navigate = useNavigate();
    const [currentStep, setCurrentStep] = useState(1);
    const [formData, setFormData] = useState({
        identity: {
            name: '',
            age: 15,
            species: 'Human',
            appearance: '',
            pronouns: ''
        },
        personality: {
            description: '',
            biggest_flaw: '',
            greatest_strength: '',
            conflict_handling: '',
            relationships: ''
        },
        interests: {
            time_spent: '',
            obsessions: '',
            collections: '',
            media: '',
            creations: ''
        },
        backstory: {
            life_story: '',
            defining_event: '',
            guardian_relationship: '',
            deepest_want: ''
        },
        hidden_questions: {
            sacrifice: '',
            expertise: '',
            reliance: '',
            time_perception: '',
            hidden_depths: '',
            problem_response: ''
        },
        session: {
            multiplayer: false,
            player_names: [],
            experience_type: 'Balanced',
            permadeath: 'Embrace it',
            content_flags: ''
        }
    });

    const updateField = (section, field, value) => {
        setFormData(prev => ({
            ...prev,
            [section]: {
                ...prev[section],
                [field]: value
            }
        }));
    };

    const handleNext = () => {
        if (currentStep < TOTAL_STEPS) {
            setCurrentStep(currentStep + 1);
            window.scrollTo(0, 0);
        }
    };

    const handlePrevious = () => {
        if (currentStep > 1) {
            setCurrentStep(currentStep - 1);
            window.scrollTo(0, 0);
        }
    };

    const handleSubmit = () => {
        localStorage.setItem(DRAFT_KEY, JSON.stringify(formData));
        navigate('/lobby');
    };

    const renderSection = () => {
        switch (currentStep) {
            case 1:
                return (
                    <FormSection
                        title="Identity"
                        description="Let's start with the basics. Who is your character?"
                    >
                        <div className="form-group">
                            <label htmlFor="name">Name *</label>
                            <input
                                type="text"
                                id="name"
                                value={formData.identity.name}
                                onChange={(e) => updateField('identity', 'name', e.target.value)}
                                placeholder="Full name, nicknames welcome"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="age">Age</label>
                            <input
                                type="number"
                                id="age"
                                value={formData.identity.age}
                                onChange={(e) => updateField('identity', 'age', parseInt(e.target.value) || 15)}
                                min="1"
                                max="99"
                            />
                            <small>Teenagers (13-17) are default, but any age is fine</small>
                        </div>

                        <div className="form-group">
                            <label htmlFor="species">Species</label>
                            <select
                                id="species"
                                value={formData.identity.species}
                                onChange={(e) => updateField('identity', 'species', e.target.value)}
                            >
                                <option value="Human">Human</option>
                                <option value="Troll">Troll</option>
                                <option value="Cherub">Cherub</option>
                                <option value="Carapacian">Carapacian</option>
                                <option value="Custom">Custom</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label htmlFor="appearance">Appearance</label>
                            <textarea
                                id="appearance"
                                value={formData.identity.appearance}
                                onChange={(e) => updateField('identity', 'appearance', e.target.value)}
                                placeholder="Describe what your character looks like..."
                                rows="4"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="pronouns">Pronouns</label>
                            <input
                                type="text"
                                id="pronouns"
                                value={formData.identity.pronouns}
                                onChange={(e) => updateField('identity', 'pronouns', e.target.value)}
                                placeholder="e.g., they/them, she/her, he/him"
                            />
                        </div>
                    </FormSection>
                );

            case 2:
                return (
                    <FormSection
                        title="Personality"
                        description="Now let's dig into who your character really is."
                    >
                        <div className="form-group">
                            <label htmlFor="personality-desc">Describe your character's personality *</label>
                            <textarea
                                id="personality-desc"
                                value={formData.personality.description}
                                onChange={(e) => updateField('personality', 'description', e.target.value)}
                                placeholder="Are they outgoing or shy? Serious or playful? Organized or chaotic? Tell us about their vibe..."
                                rows="6"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="flaw">What is their biggest flaw? *</label>
                            <textarea
                                id="flaw"
                                value={formData.personality.biggest_flaw}
                                onChange={(e) => updateField('personality', 'biggest_flaw', e.target.value)}
                                placeholder="The thing they struggle with most, or that gets them into trouble..."
                                rows="4"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="strength">What is their greatest strength? *</label>
                            <textarea
                                id="strength"
                                value={formData.personality.greatest_strength}
                                onChange={(e) => updateField('personality', 'greatest_strength', e.target.value)}
                                placeholder="What they're genuinely, authentically good at..."
                                rows="4"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="conflict">How do they handle conflict? *</label>
                            <textarea
                                id="conflict"
                                value={formData.personality.conflict_handling}
                                onChange={(e) => updateField('personality', 'conflict_handling', e.target.value)}
                                placeholder="Fight, avoid, talk their way out, shut down, etc..."
                                rows="4"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="relationships">How do they relate to other people? *</label>
                            <textarea
                                id="relationships"
                                value={formData.personality.relationships}
                                onChange={(e) => updateField('personality', 'relationships', e.target.value)}
                                placeholder="Loner, loyal friend, social butterfly, guarded, etc..."
                                rows="4"
                                required
                            />
                        </div>
                    </FormSection>
                );

            case 3:
                return (
                    <FormSection
                        title="Interests & Hobbies"
                        description="What does your character care about? What fills their time?"
                    >
                        <div className="form-group">
                            <label htmlFor="time-spent">What does your character spend most of their time doing? *</label>
                            <textarea
                                id="time-spent"
                                value={formData.interests.time_spent}
                                onChange={(e) => updateField('interests', 'time_spent', e.target.value)}
                                placeholder="Their daily routine, favorite activities..."
                                rows="4"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="obsessions">What are they obsessed with? *</label>
                            <textarea
                                id="obsessions"
                                value={formData.interests.obsessions}
                                onChange={(e) => updateField('interests', 'obsessions', e.target.value)}
                                placeholder="A fandom, a hobby, a subject — the more specific the better"
                                rows="4"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="collections">What do they collect, if anything?</label>
                            <textarea
                                id="collections"
                                value={formData.interests.collections}
                                onChange={(e) => updateField('interests', 'collections', e.target.value)}
                                placeholder="Physical items, digital files, experiences..."
                                rows="3"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="media">What media do they love?</label>
                            <textarea
                                id="media"
                                value={formData.interests.media}
                                onChange={(e) => updateField('interests', 'media', e.target.value)}
                                placeholder="Books, games, movies, music, etc..."
                                rows="3"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="creations">Do they create anything?</label>
                            <textarea
                                id="creations"
                                value={formData.interests.creations}
                                onChange={(e) => updateField('interests', 'creations', e.target.value)}
                                placeholder="Art, music, code, writing, etc..."
                                rows="3"
                            />
                        </div>
                    </FormSection>
                );

            case 4:
                return (
                    <FormSection
                        title="Backstory"
                        description="Where did your character come from? What shaped them?"
                    >
                        <div className="form-group">
                            <label htmlFor="life-story">Describe your character's life up to this point *</label>
                            <textarea
                                id="life-story"
                                value={formData.backstory.life_story}
                                onChange={(e) => updateField('backstory', 'life_story', e.target.value)}
                                placeholder="Their history, upbringing, major life events..."
                                rows="6"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="defining-event">What's the most defining event that shaped who they are today? *</label>
                            <textarea
                                id="defining-event"
                                value={formData.backstory.defining_event}
                                onChange={(e) => updateField('backstory', 'defining_event', e.target.value)}
                                placeholder="A moment, a loss, a discovery, a relationship..."
                                rows="4"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="guardian">What is their relationship with their guardian/caretaker like? *</label>
                            <textarea
                                id="guardian"
                                value={formData.backstory.guardian_relationship}
                                onChange={(e) => updateField('backstory', 'guardian_relationship', e.target.value)}
                                placeholder="Parent, sibling, mentor, or something stranger..."
                                rows="4"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="want">What do they want most in the world? *</label>
                            <textarea
                                id="want"
                                value={formData.backstory.deepest_want}
                                onChange={(e) => updateField('backstory', 'deepest_want', e.target.value)}
                                placeholder="Their deepest desire, goal, or dream..."
                                rows="4"
                                required
                            />
                        </div>
                    </FormSection>
                );

            case 5:
                return (
                    <FormSection
                        title="A Few Final Questions"
                        description="Just a few more things to help us understand your character."
                    >
                        <div className="form-group">
                            <label htmlFor="sacrifice">What would you sacrifice everything for? *</label>
                            <textarea
                                id="sacrifice"
                                value={formData.hidden_questions.sacrifice}
                                onChange={(e) => updateField('hidden_questions', 'sacrifice', e.target.value)}
                                placeholder="A person, a principle, a dream..."
                                rows="4"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="expertise">What do you know more about than almost anyone else? *</label>
                            <textarea
                                id="expertise"
                                value={formData.hidden_questions.expertise}
                                onChange={(e) => updateField('hidden_questions', 'expertise', e.target.value)}
                                placeholder="A skill, a subject, a secret..."
                                rows="4"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="reliance">Are you someone people rely on, or someone who relies on others? *</label>
                            <textarea
                                id="reliance"
                                value={formData.hidden_questions.reliance}
                                onChange={(e) => updateField('hidden_questions', 'reliance', e.target.value)}
                                placeholder="Explain your answer..."
                                rows="4"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="time">Describe a moment when time seemed to slow down or speed up for you. *</label>
                            <textarea
                                id="time"
                                value={formData.hidden_questions.time_perception}
                                onChange={(e) => updateField('hidden_questions', 'time_perception', e.target.value)}
                                placeholder="A specific memory or experience..."
                                rows="4"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="hidden">What's something most people don't know about you? *</label>
                            <textarea
                                id="hidden"
                                value={formData.hidden_questions.hidden_depths}
                                onChange={(e) => updateField('hidden_questions', 'hidden_depths', e.target.value)}
                                placeholder="A secret, a talent, a fear..."
                                rows="4"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="problem">When things go wrong, do you look for someone to blame, something to fix, or a way to escape? *</label>
                            <textarea
                                id="problem"
                                value={formData.hidden_questions.problem_response}
                                onChange={(e) => updateField('hidden_questions', 'problem_response', e.target.value)}
                                placeholder="Describe your typical response..."
                                rows="4"
                                required
                            />
                        </div>
                    </FormSection>
                );

            case 6:
                return (
                    <FormSection
                        title="Session Preferences"
                        description="Tell the Game Master what kind of experience you're looking for."
                    >
                        <div className="form-group">
                            <label htmlFor="experience">What kind of experience are you looking for?</label>
                            <select
                                id="experience"
                                value={formData.session.experience_type}
                                onChange={(e) => updateField('session', 'experience_type', e.target.value)}
                            >
                                <option value="Story-focused">Story-focused</option>
                                <option value="Combat-heavy">Combat-heavy</option>
                                <option value="Puzzle-oriented">Puzzle-oriented</option>
                                <option value="Balanced">Balanced</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label>How do you feel about permadeath?</label>
                            <div className="radio-group">
                                <label>
                                    <input
                                        type="radio"
                                        name="permadeath"
                                        value="Embrace it"
                                        checked={formData.session.permadeath === 'Embrace it'}
                                        onChange={(e) => updateField('session', 'permadeath', e.target.value)}
                                    />
                                    Embrace it (full Sburb experience)
                                </label>
                                <label>
                                    <input
                                        type="radio"
                                        name="permadeath"
                                        value="Soften it"
                                        checked={formData.session.permadeath === 'Soften it'}
                                        onChange={(e) => updateField('session', 'permadeath', e.target.value)}
                                    />
                                    Soften it (some safety nets)
                                </label>
                                <label>
                                    <input
                                        type="radio"
                                        name="permadeath"
                                        value="Avoid it"
                                        checked={formData.session.permadeath === 'Avoid it'}
                                        onChange={(e) => updateField('session', 'permadeath', e.target.value)}
                                    />
                                    Avoid it (no permanent death)
                                </label>
                            </div>
                        </div>

                        <div className="form-group">
                            <label htmlFor="content-flags">Anything you want to avoid in this game? (optional)</label>
                            <textarea
                                id="content-flags"
                                value={formData.session.content_flags}
                                onChange={(e) => updateField('session', 'content_flags', e.target.value)}
                                placeholder="Content warnings, topics to avoid, etc..."
                                rows="3"
                            />
                        </div>
                    </FormSection>
                );

            case 7:
                return <CharacterReview formData={formData} />;

            default:
                return null;
        }
    };

    return (
        <div className="character-creator">
            <h1>Sburb Character Creator</h1>
            <p className="creator-intro">
                Welcome to the Sburb Character Creator. This questionnaire will help the Game Manager understand your character's soul.
            </p>

            <ProgressIndicator currentStep={currentStep} totalSteps={TOTAL_STEPS} />

            {renderSection()}

            <div className="wizard-navigation">
                {currentStep > 1 && (
                    <button onClick={handlePrevious} className="btn-secondary">
                        ← Previous
                    </button>
                )}

                {currentStep < TOTAL_STEPS && (
                    <button onClick={handleNext} className="btn-primary">
                        Next →
                    </button>
                )}

                {currentStep === TOTAL_STEPS && (
                    <button onClick={handleSubmit} className="btn-submit">
                        Submit Character
                    </button>
                )}
            </div>
        </div>
    );
}

export default CharacterCreator;
