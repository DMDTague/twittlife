from models import GameState, Entity, Event, LongTermMemory, ShortTermMemory, TraitMatrix
from engine import GameEngine
import uuid

def run_tests():
    print("Initializing Game State...")
    state = GameState()
    engine = GameEngine(state)

    player = Entity(
        id="player_1",
        name="Alex",
        is_player=True,
        archetype="The Protagonist",
        trait_matrix=TraitMatrix(politics=80, tone=50, hostility=0)
    )
    
    npc1 = Entity(
        id="npc_1",
        name="Bob",
        archetype="The Detective",
        trait_matrix=TraitMatrix(politics=-90, tone=0, hostility=80) 
        # Bob is far left, Player is far right. Friction will be 170.
    )
    
    npc2 = Entity(
        id="npc_2",
        name="Charlie",
        archetype="The Villain",
        trait_matrix=TraitMatrix(politics=0, tone=-100, hostility=-60)
    )

    engine.add_entity(player)
    engine.add_entity(npc1)
    engine.add_entity(npc2)

    print("\n--- Event 1: Public Post ---")
    event1 = Event(
        id=str(uuid.uuid4()),
        type="tweet",
        content="Just arrived in Philadelphia! Ready to explore.",
        initiator_id="player_1",
        visibility="Public"
    )
    engine.process_action(event1)

    print("\n--- Event 2: Private Message (Player -> NPC 1) ---")
    event2 = Event(
        id=str(uuid.uuid4()),
        type="dm",
        content="Hey Bob, don't tell Charlie, but his newest tweet is dumb.",
        initiator_id="player_1",
        visibility="Private",
        target_ids=["npc_1"]
    )
    engine.process_action(event2)

    print("\nValidating Context Generation...")
    
    prompt_bob = engine.generate_llm_prompt_for_entity("npc_1")
    prompt_charlie = engine.generate_llm_prompt_for_entity("npc_2")

    print("\n=== BOB'S Context ===")
    print(prompt_bob)

    print("\n=== CHARLIE'S Context ===")
    print(prompt_charlie)

    print("\nRunning Assertions...")
    assert "don't tell Charlie" in prompt_bob, "Bob should see the private message!"
    assert "don't tell Charlie" not in prompt_charlie, "Charlie should NOT see the private message between Player and Bob! PRIVACY LEAK!"
    print("\n✅ All tests passed. Privacy filter is working correctly.")

if __name__ == "__main__":
    run_tests()
