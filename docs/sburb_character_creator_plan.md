# Sburb RPG: Character Creator — Design Planning Document

## Core Design Philosophy

### Why Players Should Not Choose Their Class and Aspect

In Homestuck, the title system is not a menu selection. It is a metaphysical truth about who a person is at their core — assigned by the game itself, which perceives the player's soul more clearly than they perceive themselves. The moment a player "chooses" to be a Knight of Time, the entire mythology collapses. A Knight doesn't choose to be a Knight. They are one, whether they know it yet or not.

This has several downstream effects on game design that reinforce each other:

**Discovery becomes a narrative arc.** If the player doesn't know their class upfront, the moment they start to realize it mid-game ("wait... am I a Thief of Light? That's... actually very me") is a genuine emotional beat. That recognition only works if it was never stated outright.

**The GM's first act of interpretation is meaningful.** Reading the character sheet and assigning a title is not a mechanical step — it's the GM performing the same role that Sburb itself performs. The GM is reading the soul of a fictional person and determining their mythological role. This should be treated with weight and care, not as a lookup table operation.

**Players can't game the system.** If the player knows that "Knight" means "cool warrior who uses their aspect as a weapon," they'll fill out the character sheet to get that. Keeping the assignment invisible prevents min-maxing a system that is explicitly not supposed to be min-maxable.

**It reflects the source material honestly.** None of the Homestuck kids chose their titles. Dave didn't decide to be a Knight. The game decided. The RPG should replicate this.

---

## Character Creator Structure

### Section 1: Identity

**Fields:**
- **Name** — Full name, nicknames welcome
- **Age** — Teenagers are default (13-17), but should be open
- **Species** — Human, troll, cherub, carapacian, or custom. Species affects some downstream generation (trolls get hemospectrum-relevant content, cherubs get unique quest structures, etc.)
- **Appearance** — Freeform text description. Will eventually inform sprite generation.
- **Pronouns** — Used throughout the game by GM and NPCs.

**Design reasoning:**
These fields are purely informational and establish who the player is before we get into anything psychologically revealing. They also anchor the GM's language for the entire session — pronouns especially need to be collected here, not assumed. Appearance description informs the sprite, which is one of the few graphical elements in the game.

---

### Section 2: Personality

**Fields:**
- **Describe your character's personality** (freeform, no word limit)
- **What is their biggest flaw?** (the thing they struggle with most, or that gets them into trouble)
- **What is their greatest strength?** (what they're genuinely, authentically good at)
- **How do they handle conflict?** (fight, avoid, talk their way out, shut down, etc.)
- **How do they relate to other people?** (loner, loyal friend, social butterfly, guarded, etc.)

**Design reasoning:**
This is the richest section for Class assignment. The Class system maps almost directly onto personality archetypes — Knights tend to be insecure overachievers who hide behind competence, Pages tend to be passive and underestimated, Seers tend to be people who see problems clearly but struggle to act on that knowledge, and so on.

The flaw question is particularly important. In Homestuck, a character's Class is often the game's way of forcing them to confront and transform their core flaw. A Thief who steals from others needs to learn generosity. A Bard who destroys through chaos needs to find purpose. Knowing the flaw upfront lets the GM design the personal quest arc immediately.

The conflict question signals active vs. passive classes. Characters who charge in tend toward Knight/Prince/Witch. Characters who observe, support, or mediate tend toward Seer/Sylph/Rogue.

---

### Section 3: Interests and Hobbies

**Fields:**
- **What does your character spend most of their time doing?**
- **What are they obsessed with?** (a fandom, a hobby, a subject — the more specific the better)
- **What do they collect, if anything?**
- **What media do they love?** (books, games, movies, music, etc.)
- **Do they create anything?** (art, music, code, writing, etc.)

**Design reasoning:**
This section drives the mechanical layer of character creation more than any other. It generates:

**Strife Specibus:** The weapon type is almost always derived from interests. A kid obsessed with baseball gets Clubkind. A programmer gets Keystrokekind or Codekind. A musician might get Drumstickekind. A chef might get Knifekind (which happens to also be Bladekind). The more specific and personal the interest, the more satisfying the Specibus.

**Fetch Modus:** Personality and interests together determine this. A chaotic character with too many hobbies might get a Pictionary Modus or Wallet Modus that makes inventory frustrating. An organized, logical character might get an Array Modus that works sensibly. A competitive gamer might get a Puzzle Modus where they have to solve something to retrieve each item.

**Alchemy starting point:** What the player has in their house at the start of the game — and therefore what early alchemy is possible — comes directly from their interests and hobbies. A collector has a bedroom full of weird objects to throw into the Alchemiter. A musician has instruments. These become their first weapons and tools.

**Land theming:** The second element of the Land name (the emotional/thematic noun) is often derived from interests. A kid who loves astronomy might end up on a Land of Stars and something. A kid who programs might have a Land of Code and something. This gives the Land personal resonance.

---

### Section 4: Backstory

**Fields:**
- **Describe your character's life up to this point** (freeform)
- **What's the most defining event that shaped who they are today?**
- **What is their relationship with their guardian/caretaker like?**
- **What do they want most in the world?**

**Design reasoning:**
The backstory primarily serves the personal quest arc. The GM needs to know what wounds the character is carrying into the game, because the game is going to make them bleed from exactly those wounds before it heals them.

The guardian relationship is a consistent Homestuck motif — every player's relationship with their guardian is complicated in a specific way, and the game forces them to confront it. A neglectful guardian creates different quest content than an overbearing one, or an absent one, or a strange inhuman one.

The "what do they want most" question is the most useful Aspect signal in the entire form, which is why it appears here rather than in a dedicated section. It doesn't feel like an Aspect-assignment question — it reads as pure character development — but it reveals what a person fundamentally values and therefore what their Aspect governs.

---

### Section 5: The Hidden Aspect Questions

These questions are framed as worldbuilding flavor or personal reflection, but they are specifically designed to triangulate Aspect assignment. They should not be labeled as "Aspect Questions." They should feel like natural character development.

**Fields:**
- **"What would you sacrifice everything for?"** — Maps to Life/Doom (things vs. principles), Hope/Rage (ideals vs. truths), Blood/Breath (relationships vs. freedom)
- **"What do you know more about than almost anyone else?"** — Maps to Light (knowledge/relevance) vs. Void (hidden things)
- **"Are you someone people rely on, or someone who relies on others?"** — Maps to active/passive class direction
- **"Describe a moment when time seemed to slow down or speed up for you."** — Time players often have a natural relationship with rhythm, urgency, or mortality
- **"What's something most people don't know about you?"** — Void players tend to have significant hidden depths; Light players tend to have public-facing identities that differ from their private selves
- **"When things go wrong, do you look for someone to blame, something to fix, or a way to escape?"** — Rage/Mind (blame) vs. Life/Sylph-type (fix) vs. Breath (escape)

**Design reasoning:**
These questions are deliberately oblique. A player who knows the Aspect system might try to answer strategically if they know what's being measured. By framing them as character introspection rather than mechanical selection, you get honest answers that actually reflect the character rather than the player's meta-game preferences.

The GM should treat these as the final input for Aspect determination, cross-referenced against everything else in the form. No single answer should determine an Aspect — it's the pattern across all answers that matters.

---

### Section 6: Session Setup

**Fields:**
- **Are you playing solo or with others?** (If with others, list player names)
- **What kind of experience are you looking for?** (Story-focused, combat-heavy, puzzle-oriented, balanced)
- **How do you feel about permadeath?** (Affects how the GM handles near-death situations pre-God Tier)
- **Anything you want to avoid in this game?** (Content flags — optional, but useful for the GM)

**Design reasoning:**
This section is purely operational. It doesn't affect title assignment but significantly affects session tone and structure. A player who wants story focus gets more NPC dialogue and quest depth. A player who wants combat gets harder, more frequent encounters. The permadeath question is important because some players understand and embrace the Sburb death system; others need it softened. The content flag question allows players to flag topics or themes they'd prefer the GM avoid, which is good practice for any RPG.

---

## GM Processing: From Character Sheet to Title

Once the character creator is complete, the GM performs the following process before the session starts. The player never sees this process.

### Step 1: Read Everything Twice

The first read is for general impression. The second read is for pattern recognition. The GM is looking for recurring themes, contradictions, and the shape of the character's soul.

### Step 2: Assign the Aspect First

The Aspect is the easier of the two assignments. Look for:

- What the character fundamentally values or fears
- What their hidden questions cluster around
- What "what would you sacrifice everything for" reveals
- Whether they gravitate toward internal (Heart, Mind, Hope, Rage, Doom, Life) or external (Time, Space, Light, Void, Breath, Blood) concerns

**Aspect Signal Examples:**
- Obsessive about fairness and justice? → Mind
- Deeply relationship-defined, can't function without their people? → Blood
- Loner who secretly longs for freedom from obligation? → Breath
- Wants to be seen, to matter, to leave a legacy? → Light
- Comfortable with darkness, secrets, things unsaid? → Void
- Fundamentally optimistic, believes in people? → Hope or Life
- Cynical, cuts through false comfort easily? → Rage or Doom
- Time-anxious, aware of mortality, obsessed with efficiency? → Time
- Creator, builder, caretaker, nurturer? → Space or Life

### Step 3: Assign the Class

The Class maps onto behavioral pattern and relationship to their Aspect. Key questions:

**Does this character use their Aspect actively or does it work through them?**
- Active (Knight, Prince, Witch, Thief, Mage, Heir) vs. Passive (Page, Bard, Sylph, Rogue, Seer, Maid)

**Does this character serve others or take for themselves?**
- Service/support orientation → Sylph, Rogue, Maid, Seer
- Self-oriented/assertive → Knight, Prince, Witch, Thief

**What is their relationship to their core flaw?**
- Hides behind competence? → Knight
- Destroys what they touch despite good intentions? → Bard or Prince
- Takes what they need without enough guilt? → Thief
- Sees clearly but doesn't act? → Seer
- Fixes everything but themselves? → Sylph
- Enormous untapped potential, currently lost? → Page

**Is this character the "natural" embodiment of their Aspect, or do they have to work for it?**
- Natural, effortless → Heir
- Creates/generates it from nothing → Maid
- Manipulates and bends it to their will → Witch

### Step 3.5: Assign Lunar Sway (Prospit or Derse Dreamer)

Lunar Sway determines the player's dream moon: **Prospit** (golden city of optimism, direct truth confrontation) or **Derse** (purple spires of skepticism, internal scheming/enlightenment). It's **not** a combat binary ("Prospit = defenders/passive, Derse = aggressors/active")—that's a common misconception. Sway reflects **worldview and growth style**:

- **Prospit Dreamers**: Heart-driven optimists who grow through **inspiration, direct experience, and heroic confrontation**. Naive/idealistic at start; vulnerable dream selves (easy to murder → forces alpha growth via loss). Excel in bold, fate-embracing arcs. **Counterintuitive for aggressors**: They seek external glory/validation, thriving on "chosen one" drama.
- **Derse Dreamers**: Mind-driven skeptics who grow through **analysis, doubt, and strategic subversion**. Cynical/guarded at start; resilient but corruptible dream selves (internal tests → forces self-mastery). Excel in shadowy, questioning arcs.

**Assignment Process** (cross-reference Sections 2–5):
1. **Scan for Core Worldview**:
   - **Prospit Signals**: Idealistic flaws (naivety, overconfidence in "rightness"), direct conflict (charges in/seeks glory), relational warmth (team validation), sacrifice for "greater good/cause." Hidden Qs: External blame/fix/ideals.
   - **Derse Signals**: Cynical/guarded flaws (doubt, secrecy), indirect conflict (schemes/avoids/plans), independent loyalty (hides true self), sacrifice for "knowledge/control/security." Hidden Qs: Internal loops/hidden truths/questioning.

2. **Aspect/Class Tiebreaker** (subtle bias, not override):
   | Aspect Lean | Prospit Fit | Derse Fit |
   |-------------|-------------|-----------|
   | **Hope/Light/Space** | Strong (inspiration/fortune/creation quests) | Moderate |
   | **Void/Time/Mind** | Moderate | Strong (secrets/inevitability/choices intrigue) |
   | **Blood/Breath/Life** | Balanced | Balanced |

   | Class Lean | Prospit Fit | Derse Fit |
   |------------|-------------|-----------|
   | **Passive/Heir/Page** | Strong (heroic inheritance/growth) | Moderate |
   | **Active/Mage/Knight** | Balanced | Strong (scheming exploits) |

3. **Resolve Counterexamples** (using canon):
   - **Aggressive = Prospit?** (Vriska, Thief of Light): Glory-hungry optimist—steals for heroic relevance, embraces fate boldly. Prospit murder vulnerability mirrors her "high-risk drama" arc.
   - **Supportive = Derse?** (Roxy, Rogue of Void): Witty skeptic who schemes in shadows (void-hoards via alcohol/AI parenting), grows through internal doubt. Derse corruption risk fits her self-sabotage/redistribution tension.
   - **Other Examples**: John (Knight of Breath, Prospit): Heroic freedom-seeker. Rose (Seer of Light, Derse): Cynical analyst. Dave (Knight of Time, Derse): Ironic schemer hiding pain.

4. **Finalize & Reveal**:
   - **Prospit**: Epic quests, inspiring visions (e.g., "Golden towers call—fight for truth!").
   - **Derse**: Shadowy intrigue, doubt tests (e.g., "Purple spires whisper—question the lie!").
   - First dream: Narrative hook (Prospit: Bold defense of towers; Derse: Sneaky court schemes).

**Detailed Signal Table** (for quick GM reference):
| Sheet Element | Prospit (Optimistic/Heroic) Example | Derse (Skeptical/Strategic) Example |
|---------------|-------------------------------------|-------------------------------------|
| **Flaw**     | Overconfidence, naivety ("I can save everyone!") | Self-doubt, secrecy ("No one gets my real plan") |
| **Strength** | Charisma, direct action ("Charge in!") | Insight, planning ("I see the long game") |
| **Conflict** | Fights head-on, seeks validation | Avoids/schemes, questions motives |
| **Relations**| Craves spotlight/team glory | Loyal but independent/shadowy |
| **Sacrifice**| "Friends/cause" (external ideals) | "Knowledge/control" (internal security) |
| **Repetition**| "Push through heroically" | "Analyze to break the pattern" |
| **Hidden Depth** | Public hero, private doubts | Hidden genius, public chill |

**Edge Cases**:
- **Tie**: Default Prospit for Hope/Light (inspirational default); Derse for Void/Time (intrigue default).
- **Multiplayer Balance**: Aim 50/50; Prospit needs Derse skeptics to ground them.
- **Cool Factor**: Prospit = high-stakes heroism (murder drama); Derse = clever subversion (corruption intrigue).

This ensures sway feels mythic/earned, handles canon outliers (Vriska/Roxy), and ties to discovery (dreams reveal worldview mid-arc).

### Sprite Prototyping Assignment

#### Overview

Each player's kernelsprite must be prototyped twice: once before entering the Medium (pre-entry) and once after (post-entry). The GM assigns both prototypings during character creation based on the character sheet, though the post-entry prototyping may be adjusted later based on what happens in play.

**Critical rule:** Pre-entry prototypings affect the entire session. Whatever traits the first prototyping has, ALL underlings in the session inherit those traits. This is a session-wide balancing act, not a per-player decision.

---

#### Pre-Entry Prototyping (First Prototyping)

##### What Gets Prototyped

The first prototyping should come from the player's real-world environment — something in their house or life before the game starts. Common categories:

**Dead guardians or pets** — Emotionally heavy, narratively rich. The sprite gains knowledge and personality from the deceased. Creates strong quest hooks (confronting unresolved feelings about the dead). Canon examples: Nannasprite (John's grandmother), Jaspersprite (Rose's cat).

**Stuffed animals or toys** — Lighter, often comedic. The sprite gains a childlike or absurd personality. Less narratively weighty but can still be meaningful if the object has personal significance. Canon example: Cal (Dirk's puppet).

**Objects with personal significance** — Items tied to interests, hobbies, or obsessions from the character sheet. A musician's instrument, a programmer's laptop, a collector's prized possession. The sprite gains a personality shaped by the object's purpose or the player's relationship to it.

**Absurd or chaotic choices** — Sometimes the prototyping is just whatever was nearby or happened by accident. This is valid but should still connect to the character's life somehow — it shouldn't feel random.

##### Assignment Process

1. **Scan the character sheet for hooks:**
   - Backstory: Is there a dead guardian mentioned? A deceased pet? A defining loss?
   - Interests: What objects would be in their room? What do they collect?
   - Relationships: Who or what do they care about that could be prototyped?

2. **Check session balance:**
   - What have other players' pre-entry prototypings given to the underlings?
   - Is this prototyping going to make the game unwinnable? (e.g., prototyping something invincible)
   - Is it interesting for combat? Does it add abilities, knowledge, or just aesthetic traits?

3. **Prioritize narrative weight over mechanical advantage:**
   - A dead guardian is almost always the right choice if one exists in the backstory
   - A meaningful object beats a generic one
   - The sprite should feel personal, not optimal

##### Enemy Implications

Whatever you choose, every underling in the session inherits traits from it. Think about what this means practically:

**Dead guardian/pet** — Underlings gain knowledge, speech, potentially some personality traits. They become slightly more intelligent or gain specific memories. This is narratively interesting and mechanically manageable.

**Powerful entity** — Dangerous. If you prototype something that's already strong (a living guardian who's a fighter, a dangerous animal), underlings become significantly harder. Only do this if you want a high-difficulty session.

**Object with specific function** — Underlings gain properties of that object. A bird gives flight. A weapon gives that weapon type. A laptop might give technological abilities. Be specific about what traits transfer.

**Absurd or comedic choice** — Underlings gain aesthetic properties (color, shape, voice) without necessarily gaining functional advantages. This keeps difficulty manageable while adding flavor.

##### Naming Convention

Sprites are named by combining the prototyped entities. Pre-entry prototyping determines the first half of the name.

Examples:
- Grandmother → Nannasprite (after second prototyping: Nannasprite)
- Cat (Jaspers) → Jaspersprite
- Harlequin doll (Cal) → Calsprite

The name should be obvious from what was prototyped. Don't overthink it.

---

#### Post-Entry Prototyping (Second Prototyping)

##### What Gets Prototyped

The second prototyping happens after the player enters the Medium. It can be:
- An object or creature found on the player's Land
- An object from the player's transported house
- A consort or other NPC (though this is rare and problematic)
- The player themselves (very rare, creates a self-loop)

Unlike the first prototyping, the second **does not affect enemies**. It only changes the sprite itself.

##### Assignment Process (Flexible)

The GM can assign a default second prototyping during character creation, but this is more tentative than the first. The actual second prototyping often happens organically during play — the player finds something on their Land and throws it in, or the sprite suggests something.

**If assigning during character creation:**
- Look for thematic resonance with the Land
- Consider what would make the sprite more helpful or more cryptic
- Think about what would create interesting personality fusion

**If leaving it open:**
- Note in the sprite's file that second prototyping is pending
- Let it happen naturally during play
- The player might surprise you with their choice

##### Personality Fusion

After both prototypings, the sprite's personality is a fusion of both entities/objects. If you prototyped Grandmother + Cat, the sprite acts like a grandmother who is also somewhat cat-like. If you prototyped Laptop + Consort, the sprite is a technological salamander with computer knowledge.

The fusion should be:
- Coherent enough to roleplay consistently
- Strange enough to feel alien
- Useful enough to provide guidance (cryptically)
- Personal enough to create emotional moments

---

#### Sprite Knowledge and Personality

##### What Sprites Know

Sprites have knowledge about Sburb's mechanics that players don't. They know:
- The basic structure of the game (Lands, Denizens, Gates)
- The player's role in mythological terms (though they may speak in riddles)
- Some information about Skaia, Prospit, Derse
- Quest-relevant hints tied to the player's personal journey

**What they don't know or won't say directly:**
- Specific solutions to puzzles
- Exact outcomes of choices
- How to "win" in concrete terms
- Information that would short-circuit the player's growth arc

##### How Sprites Talk

Sprites are cryptic, not because they're trying to be annoying, but because they exist slightly outside linear time and see possibilities rather than certainties. They speak in:
- Metaphors and riddles
- References to things the player doesn't understand yet
- Hints that only make sense in retrospect
- Emotional or mythological language rather than mechanical language

**Bad sprite dialogue:**
> "You need to reach Level 10 and defeat the Denizen to proceed."

**Good sprite dialogue:**
> "The serpent coiled in the deep waits for one who has climbed high enough to see the truth of their own reflection. But you are still looking at the ground, child."

##### Prototyping-Specific Personality Traits

The personality should clearly derive from what was prototyped:

**Dead guardian/pet:**
- Familiar mannerisms and speech patterns from life
- Concern for the player's wellbeing (potentially overbearing)
- Grief/unresolved business as subtext
- Knowledge they had in life + game knowledge

**Object:**
- Personality shaped by the object's function or the player's relationship to it
- A guitar sprite might speak in musical metaphors
- A book sprite might be scholarly and verbose
- Absurd objects create absurd personalities

**Fusion:**
- Both components visible in how they act and speak
- Contradictions between the two create interesting tension
- Neither fully dominates unless one is much more "alive" than the other

---

#### Session-Wide Coordination (Multiplayer)

In multiplayer sessions, the GM must consider all pre-entry prototypings together before finalizing any of them.

##### Balance Check

If Player A's sprite is prototyped with a dead grandmother (knowledge, speech) and Player B's sprite is prototyped with a laser cannon (ranged attacks, high damage), all underlings in the session get:
- The grandmother's knowledge and speech
- Laser attacks

This might be manageable or it might make early combat impossible. Adjust before the session starts.

##### Difficulty Calibration

You can tune session difficulty through prototyping:
- **Low difficulty**: Mostly aesthetic or knowledge-based prototypings (dead relatives, objects with personality but no combat abilities)
- **Medium difficulty**: Mix of knowledge and functional abilities (a pet that can fly, a weapon that's not too powerful)
- **High difficulty**: Multiple combat-functional prototypings (weapons, dangerous animals, powerful entities)

##### Avoid Session-Breaking Combinations

Some prototypings break the game if combined:
- Multiple invincible/invulnerable entities
- Multiple sources of instant-kill abilities
- Combinations that make underlings literally unbeatable

If you see this happening, adjust one or more prototypings to keep the session viable.

---

#### Template: Sprite File (During Character Creation)

When the GM assigns a sprite, create a file for it immediately:

**Filename:** `npcs/sprites/[player_name]sprite.md`

**Content:**
```markdown
# [Sprite Name]

## Identity
- **Owner:** [Player Name]
- **Pre-Entry Prototyping:** [What was prototyped + when]
- **Post-Entry Prototyping:** [Pending / Assigned / What was prototyped]

## Prototyping Details

### First Prototyping: [Entity/Object Name]
- **What it was:** [Description]
- **Why chosen:** [Narrative reasoning from character sheet]
- **Traits granted to underlings:** [List of properties all enemies now have]
- **Knowledge gained:** [What the sprite knows from this]
- **Personality contribution:** [How this shapes the sprite's behavior]

### Second Prototyping: [Entity/Object Name or "Pending"]
- **What it was:** [Description]
- **When it happened:** [During play / Pre-assigned]
- **Personality contribution:** [How this combines with the first]

## Personality

**Core Traits:** [Describe how they act, informed by both prototypings]

**Speech Pattern:** [How they talk — formal, casual, riddling, specific quirks]

**Relationship with Player:** [How they feel about their player specifically]

**Emotional Undertones:** [Subtext — grief, joy, confusion, purpose]

## Knowledge

**What They Know:**
- Game mechanics: [General Sburb knowledge]
- Player's quest: [What they can hint at]
- Mythological role: [Class/Aspect understanding, spoken cryptically]

**What They Won't Say Directly:** [Things they know but will only hint at]

## Current Status
- **Location:** [Where they are — usually following the player]
- **Mood:** [Current emotional state]
- **Recent conversations:** [Track what's been discussed]

## Last Updated
[Timestamp]
```

---

#### Examples

##### Example 1: Dead Guardian

**Character:** Jane, whose grandmother died when she was young. The backstory mentions Jane never got to say goodbye and still has her grandmother's cookbook.

**Pre-entry prototyping:** Grandmother (remains, photograph, or ashes in the house)

**Reasoning:** Strong narrative hook. Jane has unresolved grief. The sprite can provide both game guidance and emotional closure arc.

**Enemy implication:** Underlings gain speech and some of grandmother's knowledge. They might quote recipes or give advice while fighting. Manageable difficulty increase, high narrative interest.

**Sprite personality:** Warm, overbearing, speaks in cooking metaphors. Wants Jane to succeed but also wants her to process the grief.

**Post-entry prototyping (suggested):** A consort from her Land, creating a grandmother-salamander fusion. Alternately, left open for player choice.

---

##### Example 2: Meaningful Object

**Character:** Alex, a programmer whose character sheet lists "building robots" as their main hobby. Their room would be full of circuit boards and half-finished machines.

**Pre-entry prototyping:** Alex's first completed robot (a small wheeled bot)

**Reasoning:** Personal significance without the emotional weight of death. Reflects the character's interests directly.

**Enemy implication:** Underlings gain wheels/mobility, possibly minor technological abilities (beeping, LED eyes). Aesthetic more than functional — manageable.

**Sprite personality:** Logical, robotic speech patterns, but with traces of Alex's personality in how it was built. Speaks in technical metaphors.

**Post-entry prototyping (suggested):** A piece of the Land's environment (if the Land is mechanical) or a consort, creating a robot-salamander. Alternately, open.

---

##### Example 3: Absurd Accident

**Character:** Sam, whose backstory mentions their cat knocked over a lamp right before entry.

**Pre-entry prototyping:** The lamp

**Reasoning:** Accidental but still tied to their life (it's their lamp, in their room). Less narratively heavy but allows for comedic sprite personality.

**Enemy implication:** Underlings glow. They're easier to see, which is actually a slight disadvantage for them (less ambush potential). Aesthetic change, minimal mechanical impact.

**Sprite personality:** Illuminating in the literal sense, philosophical about "shedding light on truth," puns constantly. Annoying but helpful.

**Post-entry prototyping (suggested):** Sam's actual cat (who made it through entry somehow), creating the lamp-cat sprite Sam should have had if the cat hadn't knocked the lamp over first. This creates a fun narrative irony.

---

#### Summary Checklist

When assigning sprites during character creation:

- [ ] Read character sheet for deceased guardians/pets
- [ ] Read interests for meaningful objects in their environment  
- [ ] Assign pre-entry prototyping with narrative weight prioritized
- [ ] Check what traits this gives to ALL underlings in the session
- [ ] Verify session difficulty is manageable with all prototypings combined
- [ ] Create sprite file with personality, knowledge, speech pattern
- [ ] Suggest or leave open post-entry prototyping
- [ ] Ensure sprite name follows [Entity]sprite convention

### Step 4: Assign the Specibus

Derived almost entirely from Section 3. Default to the most specific, personally resonant weapon type possible. "Swordkind" is boring. "Knitting Needlekind" for a character who knits obsessively is perfect. Always err toward the specific and personal over the generic and powerful.

### Step 5: Assign the Fetch Modus

Match to personality from Section 2. A highly organized, logical character gets a reasonable modus. A chaotic, impulsive character gets something that makes inventory management actively frustrating. This is also a source of comedy — a character who answers everything emotionally might get Emotional Resonance Modus, where they can only retrieve items they have strong feelings about.

### Step 6: Generate the Land

**First element (physical/environmental):** Derived from Aspect color palette and physical themes, plus some influence from interests. Time = red, clockwork, rhythm. Space = white, vast, open. Void = dark, deep, oceanic. Light = gold, illuminated, exposed.

**Second element (thematic/quest):** Derived from the character's core flaw or the emotional theme of their personal quest. A character whose flaw is pride might end up on a Land of [Environment] and Mirrors. A character who struggles with isolation might end up on a Land of [Environment] and Silence.

**Consort species:** Loosely tied to Land theme and player personality. Salamanders for gentle, curious players. Turtles for slow, deliberate players. Crocodiles for aggressive or territorial players. Iguanas for laid-back, sunny players.

**Denizen:** Matched to Aspect from the canonical list. The Denizen's choice should directly challenge the character's core flaw as identified in the character sheet.

### Step 7: Outline the Personal Quest Arc

Before the session begins, the GM should have a rough three-act structure for the personal quest:

- **Act 1 (early game):** The flaw is present but not yet challenged. The character operates in their comfort zone.
- **Act 2 (mid game):** The game forces situations where the flaw is a genuine liability. Things go wrong specifically because of who this character is.
- **Act 3 (late game / God Tier):** The character must actively choose to confront and transform the flaw to progress. The Denizen's choice is the climax of this arc.

---

## What the Player Experiences vs. What the GM Knows

| Element | Player Knows | GM Knows (Hidden) |
|---|---|---|
| Class | Discovers slowly through play | Assigned at session start |
| Aspect | Discovers slowly through play | Assigned at session start |
| Land Name | Told on entry | Pre-generated |
| Land Theme | Discovers through exploration | Pre-planned |
| Denizen Identity | Discovers in late game | Known from start |
| Personal Quest Theme | Emerges through play | Pre-planned |
| Strife Specibus | Told at game start | Pre-assigned |
| Fetch Modus | Told at game start | Pre-assigned |

The player is told their Specibus and Modus immediately because these are mechanical facts they need to play. The Class and Aspect are never stated outright by the GM — the player should infer them through their powers developing, their sprite's cryptic comments, and their own self-recognition.

---

## UI Considerations

### Form Flow

The character creator should feel like a questionnaire, not a stat-allocation screen. No dropdowns for Class or Aspect should exist anywhere. Ideally the form uses mostly freeform text fields, with a few structured questions (species, pronouns, session type) where a select makes sense.

**Suggested section flow:**
1. Identity (name, age, species, appearance, pronouns)
2. Personality (freeform + structured questions)
3. Interests and hobbies (mostly freeform)
4. Backstory (freeform)
5. The hidden Aspect questions (presented as "a few final questions about your character")
6. Session setup (practical options)

**Visual tone:** The form should feel like a Pesterchum profile or a Tumblr "about me" page — informal, a little playful, but with enough structure to capture what the GM needs. Avoid anything that feels like a D&D character sheet. This is not that kind of game.

### After Submission

Once the player submits, the GM processes the form silently. The player should see something like:

> "Your information has been processed by the Sburb server. Your session is being initialized. Stand by."

Then the game begins. The GM never confirms or denies the player's suspicions about their title, and never explicitly announces it. If the player asks directly ("Am I a Knight of Time?"), the GM defers:

> "That's not information the game provides directly. You'll understand your role as your journey unfolds."

---

## Edge Cases and Problems to Anticipate

### "My character has no flaws"

Some players will fill out the personality section with idealized, flaw-free characters. This is a problem because the entire personal quest arc depends on having a real flaw to work with.

**Solution:** The GM should look for hidden flaws in the backstory or relationship sections — players who claim their character has no flaws often reveal them indirectly in how they describe backstory events. If genuinely none are apparent, assign a Class that generates flaws through the nature of its power (Thief, Prince, Bard) and let the game surface the flaw organically through play.

### "My character is already very powerful"

Some players write backstories where their character is already accomplished, skilled, and confident. This conflicts with the early-game progression system.

**Solution:** Sburb strips players of their real-world advantages. A professional athlete is still weak to imps until they've climbed their Echeladder. A genius hacker's skills don't help them fight underlings. The GM should acknowledge the character's real-world competence while making clear that none of it translates directly to in-game power. This itself can be a compelling personal arc — the humbling of someone who was exceptional in the old world.

### "I want to be a Witch of Space" (player announces their title)

Some players who know Homestuck will try to declare their own title in the character sheet.

**Solution:** The GM should treat this as character information, not instruction. The player believing they're a Witch of Space is noted, but the actual assignment is made by the GM based on the full character sheet. Sometimes the player will be right — that's a satisfying moment of validation. Sometimes they'll be wrong, and discovering that is even more interesting.

### Multiplayer: Class/Aspect conflicts

In a multiplayer session, the GM should ensure:
- No two players share a Class/Aspect combination
- Aspect opposites (Time/Space, Light/Void, etc.) are ideally distributed across the group
- The party has both active and passive classes represented
- If possible, one player gets Space (for Genesis Frog breeding)

If a conflict occurs — two players' character sheets both point strongly to the same title — the GM should assign the title to whichever player it fits more strongly and find the second-best fit for the other. This trade-off should never be revealed to either player.

---

## Summary: Why This Approach Works

The character creator described here prioritizes three things above all else:

**Authenticity of character.** By collecting information about who the character actually is rather than what mechanical role the player wants to fill, the game generates characters that feel real and grounded. Their title emerges from their truth, not from a menu.

**Discovery as gameplay.** The player's gradual realization of their own mythological role is one of the most satisfying experiences the game can offer. The character creator protects that experience by keeping the title hidden until it can be meaningfully revealed through play.

**The GM as interpreter, not engine.** The AI Game Manager is not just filling in a template — it is reading a person and making a judgment call about their soul. That's a meaningful, interesting task that produces better output than mechanical title assignment. The character creator is designed to give the GM the richest possible input for that task.
