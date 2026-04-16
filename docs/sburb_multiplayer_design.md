# Sburb RPG: Multiplayer Design Document

## Overview

This document outlines the multiplayer design for the Sburb RPG, covering player interaction models, party mechanics, shared interfaces, and session structure. The guiding principle throughout is that the UI mechanics and the fiction should be the same thing — how players interact with each other technically should mirror how their characters interact with each other narratively.

---

## Session Structure

### Joining a Session

Players join a shared session using a session code. Once all players have joined and completed the character creator, the session starts simultaneously for everyone.

This deliberately omits the server/client chain mechanic from Homestuck (where one player had to set up another's equipment before they could enter the Medium). While that mechanic is lore-accurate, it is opaque to players unfamiliar with Homestuck and would create a confusing onboarding experience. The interdependence it established is achieved through other means in this design — the party system, gate progression, the Space player's Genesis Frog responsibilities, and cooperative combat.

**Optional flavor:** The GM's opening narration can acknowledge the two-disk system as pure atmosphere ("your copy of Sburb arrived in the mail with two disks — you've sent the other to [Player]") without requiring players to act on it.

### Entry Order

Entry order into the Medium is determined by character creator completion — whoever finishes first enters first. This has no mechanical advantage but creates a slight narrative stagger, which the GM can use to establish that players are experiencing the same event from slightly different moments.

---

## Interaction Models

The core design principle is that **players have different interaction models depending on their narrative relationship to each other**. There is no single multiplayer mode — the game shifts between models as the fiction demands.

### Model 1: Separate Planets (Solo Play)

When players are on their own Lands, they are effectively playing solo. Each player interacts with the GM independently at their own pace, with no synchronization required. There is no staging window, no turn order, no waiting.

The only connection between players during this phase is the **pesterlog** — the in-character messaging system that mirrors Homestuck's own Pesterchum interface. Players can talk to each other as their characters would, but they cannot see each other's GM interactions or actions. This is intentional: they are on different planets. They have no window into each other's world except communication.

This phase should feel like playing a single-player RPG that occasionally gets interrupted by a friend texting you about what's happening on their end.

### Model 2: Same Planet, Same Context (Party Play)

When players cross gates and meet on each other's Lands — or share any narrative context, such as fighting the same enemy or talking to the same NPC — they form a **party** and the interaction model shifts.

Party play introduces the **staging window**: a shared panel where both players can see each other's actions being drafted in real time, before either has been submitted to the GM. This is an abstraction of physical co-presence. In a real room, you can see your friend reaching for something. The staging window replicates that.

**Key properties of the staging window:**
- Visible only when players are narratively together in the same context
- Shows what the other player is currently drafting, live
- Does not lock or prevent either player from submitting
- Disappears or collapses during solo play, reappearing when players share a location (which itself serves as a subtle signal that something has changed)

### Submission and Conflict Resolution

There is no lock-in mechanic. Players submit when they're ready, independently. The GM processes actions in the order they arrive by server timestamp.

The staging window gives players the information to self-coordinate, but acting on that information quickly is their responsibility. Attentiveness and speed become meaningful player skills independent of character stats — if you see your party member going for the same item and you don't react in time, that's on you.

**Clear winner:** When one submission arrives meaningfully before the other, the GM narrates a clean outcome:

> "You reach for the sword, but [Player A] already has it — they were a half-second faster."

**Contested actions:** When two submissions arrive close together, rather than silently denying one player, the GM treats the conflict as a **new in-universe situation** that both players now have to deal with. The contested object or action becomes a scene rather than a tiebreak.

> "You both close your fingers around the hilt at the same moment. Neither of you lets go."

From here the GM resolves the contest through one of three methods, chosen based on context:

**Character attributes.** Relevant stats from the character sheet — strength, dexterity, a specific skill — determine the outcome cleanly and fairly. This rewards players who built characters suited to the situation.

> "Your grip tightens — but [Player A]'s strength outclasses yours by a significant margin. The sword slides out of your fingers."

**Environmental intervention.** The world takes advantage of the distraction. An imp steals the grist while both players are occupied. A consort grabs the sword to stop the argument. The item falls into a pit during the scuffle. This punishes both players equally for failing to coordinate through the staging window, which is exactly the right incentive — pay attention to what your party member is doing, or the world capitalizes on the gap.

> "While you're both pulling at the sword, an imp seizes the opportunity. It snatches your grist pouch and bolts."

**Player escalation.** The GM presents the standoff and lets both players decide what happens next. Do you let go? Do you fight for it? This turns a mechanical conflict into a roleplay moment — often the best possible outcome.

> "You're both holding the sword. [Player A] isn't letting go. What do you do?"

The GM should weight these options by context. In active combat, environmental intervention makes sense — something external capitalizes on the distraction. In a calmer scene, character attributes or player choice are more appropriate. The broader principle is that **the world reacts to player behavior**: poor coordination isn't penalized by a silent denial, it's penalized by the fiction becoming more complicated.

---

## Broadcast Events

Some events affect the entire session regardless of where players are or what they're doing. These are **universe-wide broadcasts** — environmental intrusions that every player experiences simultaneously, unprompted.

### What Triggers a Broadcast

- A player ascends to God Tier
- A player dies permanently
- The Black King awakens or is defeated
- A Forge is lit
- The Genesis Frog reaches maturity
- The universe is created (session end)
- Other GM-determined session milestones

### How Broadcasts Feel

Broadcasts are distinct from normal GM output in both content and presentation. Normal GM output is a response to something the player did. A broadcast is the universe acting on the player without being asked.

**Visually**, broadcasts should interrupt whatever the player is currently looking at — not as a pesterlog message, not as part of the local GM interaction panel, but as a separate environmental layer. Different typography, different color, no input prompt. It happens and then fades, returning the player to where they were.

**In content**, broadcasts can be calibrated to significance:

- **Minor ripple:** A subtle environmental change across all Lands. Consorts murmur. A new constellation appears. The wind shifts. Players may not immediately know what caused it.
- **Major event:** God Tier ascension, permanent death, the Black King awakening. Full interruption. Unmistakable imagery — the symbol of the relevant Aspect appearing in the sky of every Land, fireflies across every planet, etc.
- **Session-ending event:** The GM takes over every player's screen for a closing sequence.

### Information and Mystery

Broadcasts deliberately withhold explanation. The universe announces that something happened; it does not always say what or who caused it. A symbol appears in the sky — players who want to know what it means have to talk to each other through the pesterlog.

> "Did you see that? What was that symbol?"

This keeps solo-planet players emotionally invested in each other's journeys even when they can't interact directly. It also creates natural pesterlog conversations and preserves the sense that the session is a shared world, not a collection of parallel single-player games.

**Technically**, broadcasts are a websocket push from the server to all connected clients — straightforward to implement with something like Pusher or Socket.io. The GM writes the broadcast as part of its state update when a milestone is detected, and the server fans it out to all active sessions.

---

## The Pesterlog

The pesterlog is the primary social layer of the game and the only interaction available to players on separate planets. It should feel like Pesterchum — informal, in-character, slightly chaotic.

**Properties:**
- Always available regardless of location or phase
- In-character communication between player characters (not meta coordination)
- Becomes part of the GM's context when players share a scene — the GM knows what they've said to each other
- The only window into another player's world during solo-planet phases

The pesterlog and the staging window are visually and functionally distinct. The pesterlog is character-to-character communication. The staging window is a meta-layer showing what actions are being drafted. Players should never confuse the two.

---

## The Server/Client Mechanic (Omitted)

Homestuck's server/client chain — where one player sets up another's equipment before they can enter the Medium — has been deliberately excluded from this design.

**Why:** It is opaque to players unfamiliar with Homestuck, creates an uneven pre-game experience, and requires a dedicated UI mode (the server player's god-game interface) that adds significant implementation complexity. New players dropped into this system with no context would find it confusing and potentially offputting.

**What replaces it:** The interdependence the mechanic was designed to create is established through other systems — the party mechanic, gate progression requiring cooperative effort, the Space player's unique role in Genesis Frog breeding, and shared combat requiring coordination. Players become dependent on each other through play rather than through a pre-entry setup phase.

---

## Summary: Interaction Model by Phase

| Phase | Players | Interaction Model | Shared UI |
|---|---|---|---|
| Lobby | All | Session code, character creator | None |
| Separate Lands | Solo | Independent, async | Pesterlog only |
| Same Land, same context | Party | Real-time, order-of-submission | Staging window + pesterlog |
| Universe-wide event | All | Broadcast interruption | Broadcast overlay |
| Session end | All | GM cinematic sequence | Full takeover |
