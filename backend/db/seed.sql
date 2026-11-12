-- Seed stories matching the topics in data/samples:
-- signals, nodes and scenes, and scene instancing.
-- Safe to run more than once: stories are matched on title and skipped if present.

INSERT INTO user_stories (title, story, acceptance_criteria, source) VALUES
(
    'Connect a signal to a node in the editor',
    'As a developer, I want to connect a node''s signal to a receiver method in the Signals dock so that my game reacts to events like a button press without writing connection code.',
    E'- Selecting a node shows its available signals in the Signals dock.\n- Double-clicking a signal such as "pressed" opens the connection window.\n- Connecting generates a receiver method named like _on_button_pressed on the target node.\n- Pressing the button at runtime calls the receiver method.',
    'signals.txt'
),
(
    'Connect a signal to a node via code',
    'As a developer, I want to connect a signal from a script using connect() so that I can wire up nodes that I create or instantiate at runtime.',
    E'- A reference to the target node is obtained in _ready() with get_node().\n- Calling connect() on the signal, such as a Timer''s timeout, registers the callback.\n- The callback runs each time the signal is emitted.\n- The callback follows the _on_node_name_signal_name naming convention.',
    'signals.txt'
),
(
    'Define and emit a custom signal',
    'As a developer, I want to declare my own signal and emit it from a script so that other nodes can react to game events such as the player''s health reaching zero.',
    E'- A script declares a signal such as health_depleted.\n- Calling emit() on the signal notifies every connected listener.\n- Custom signals appear in the Signals dock and connect like built-in ones.\n- Signal names use a past-tense action verb.',
    'signals.txt'
),
(
    'Pass arguments with a signal',
    'As a developer, I want to emit values along with a signal so that listeners receive details such as the old and new health value.',
    E'- A signal can declare arguments, such as health_changed(old_value, new_value).\n- Extra arguments passed to emit() are delivered to the receiver method.\n- Declared argument names show in the Signals dock.',
    'signals.txt'
),
(
    'Toggle a node''s motion with a button signal',
    'As a developer, I want a Button''s pressed signal to toggle a Sprite2D''s processing so that the player can start and stop the sprite''s motion.',
    E'- The Button''s pressed signal is connected to a method on the Sprite2D.\n- The method calls set_process(not is_processing()).\n- Pressing the button once stops the sprite; pressing it again resumes motion.',
    'signals.txt'
),
(
    'Build a character from a tree of nodes',
    'As a developer, I want to combine nodes as children of one another so that I can build complex behavior, such as a character the camera follows, from simple building blocks.',
    E'- A node can be added to another node as a child.\n- A CharacterBody2D, Sprite2D, Camera2D and CollisionShape2D combine into one playable character.\n- Each node has a name and editable properties.\n- The nodes form a tree shown in the Scene dock.',
    'nodes_and_scenes.rst'
),
(
    'Change a node''s properties in the Inspector',
    'As a developer, I want to edit a node''s properties in the Inspector so that I can change how it looks and behaves, such as setting a Label''s text to "Hello World".',
    E'- Selecting a node shows its properties in the Inspector dock.\n- Editing the Text property of a Label updates the text drawn in the viewport as I type.\n- The changed value is used when the scene runs.',
    'nodes_and_scenes.rst'
),
(
    'Create and save my first scene',
    'As a developer, I want to create a scene with a root node and save it as a file so that I can load it later and use it like a new node type.',
    E'- A new scene can start with a 2D Scene, 3D Scene, User Interface or other root node.\n- A scene always has exactly one root node.\n- The scene saves to a .tscn file inside the project.\n- The Run Current Scene button runs the saved scene in a new window.',
    'nodes_and_scenes.rst'
),
(
    'Set the project''s main scene',
    'As a developer, I want to choose a main scene so that Godot loads it first whenever I or a player runs the game.',
    E'- Pressing Run Project prompts for a main scene when none is set.\n- Selecting a scene such as label.tscn sets it as the main scene.\n- The main scene path is saved in project.godot.\n- Running the project loads the main scene, which is distinct from running the current scene.',
    'nodes_and_scenes.rst'
),
(
    'Instance a scene as a child of another node',
    'As a developer, I want to instantiate a saved scene inside another scene so that I can reuse it, such as adding several Ball instances to the Main scene.',
    E'- The Instance Child Scene button adds a saved scene as a child of the selected node.\n- An instance appears as a single node with its internals hidden.\n- Each duplicate gets a unique name.\n- Every instance starts with the same structure and properties as the packed scene.',
    'instancing.md'
),
(
    'Edit a scene template and override one instance',
    'As a developer, I want to change a packed scene''s defaults and also override individual instances so that I can update all copies at once or tweak just one.',
    E'- Changing a property in ball.tscn and saving updates every instance of the Ball.\n- Changing a property on a single instance overrides the value from the packed scene.\n- A revert icon appears next to an overridden property and restores the saved value when clicked.\n- Resources such as PhysicsMaterial must be made unique before editing on one instance.',
    'instancing.md'
),
(
    'Structure a game as nested scene instances',
    'As a developer, I want to design my game as scenes that instantiate other scenes so that I can focus on game logic instead of abstract architecture.',
    E'- Each element a player sees, such as a room, house or guard, is its own scene.\n- Larger scenes, such as a citadel, instantiate smaller ones.\n- Instances can be created in the editor or from code.\n- Adding a new element only requires creating and instantiating another scene.',
    'instancing.md'
)
ON CONFLICT (title) DO NOTHING;
