from typing import List
from models import Event

def filter_events_for_entity(entity, events: List[Event]) -> List[Event]:
    """
    Returns only the events that the given entity is allowed to see based on strict privacy rules and block logic.
    """
    visible_events = []
    
    # Handle both full Entity objects or just the ID string temporarily
    entity_id = entity.id if hasattr(entity, 'id') else entity
    blocked_list = entity.blocked_list if hasattr(entity, 'blocked_list') else []
    
    for event in events:
        if event.initiator_id in blocked_list:
            continue
            
        if event.visibility == 'Public':
            visible_events.append(event)
        elif event.visibility == 'Private':
            if entity_id == event.initiator_id or entity_id in event.target_ids:
                visible_events.append(event)
        elif event.visibility == 'Sub-group':
            if entity_id == event.initiator_id or entity_id in event.target_ids:
                visible_events.append(event)
    return visible_events


# --- Phase 17: Neighborhood Hub Filtering ---

def filter_events_for_neighborhood(neighborhood_name: str, entities: dict, events: List[Event]) -> List[Event]:
    """
    Returns events where the initiator has a faction tag that matches the neighborhood's allowed tags.
    Also includes SYSTEM events (ads, news) so the feed isn't empty.
    """
    from dictionaries import NEIGHBORHOOD_HUBS
    hub = NEIGHBORHOOD_HUBS.get(neighborhood_name)
    if not hub:
        return []

    allowed_tags = set(hub["allowed_tags"])
    neighborhood_events = []

    for event in events:
        if event.visibility != "Public":
            continue
        if event.initiator_id == "SYSTEM":
            neighborhood_events.append(event)
            continue
        initiator = entities.get(event.initiator_id)
        if not initiator:
            continue
        # Check if the initiator's faction tags overlap with the allowed tags
        entity_tags = set(t.replace(" ", "_") for t in initiator.faction_tags)
        if entity_tags & allowed_tags:
            neighborhood_events.append(event)

    return neighborhood_events


def check_outsider_status(entity, neighborhood_name: str) -> dict:
    """
    Checks whether an entity's internal_truth aligns with the neighborhood's vibe anchors.
    Returns {"is_outsider": bool, "hostility_bonus": int, "violations": list}.
    """
    from dictionaries import NEIGHBORHOOD_HUBS
    hub = NEIGHBORHOOD_HUBS.get(neighborhood_name)
    if not hub:
        return {"is_outsider": False, "hostility_bonus": 0, "violations": []}

    violations = []
    for trait, (lo, hi) in hub["vibe_anchors"].items():
        entity_score = entity.internal_truth.get(trait, 0)
        if not (lo <= entity_score <= hi):
            violations.append(trait)

    is_outsider = len(violations) >= 2  # Outsider if you fail 2+ vibe checks
    hostility_bonus = hub["outsider_hostility_bonus"] if is_outsider else 0

    return {
        "is_outsider": is_outsider,
        "hostility_bonus": hostility_bonus,
        "violations": violations
    }
