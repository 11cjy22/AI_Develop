

extends NodeState
@export var player:player
@export var animated_sprite_2d:AnimatedSprite2D

var direction: Vector2
func _on_process(_delta : float) -> void:
	pass


func _on_physics_process(_delta : float) -> void:
	direction = GameInputEvents.movement_input()
	
	if  player.player_direction  == Vector2.UP:
		animated_sprite_2d.play("idle_back")
	elif  player.player_direction  == Vector2.RIGHT:
		animated_sprite_2d.play("idle_right")
		
	elif player.player_direction == Vector2.LEFT:
		animated_sprite_2d.play("idle_left")
		
	elif  player.player_direction  == Vector2.DOWN:
		animated_sprite_2d.play("idlefront")
	else :
		animated_sprite_2d.play("idlefront")


func _on_next_transitions() -> void:
	GameInputEvents.movement_input()
	
	if GameInputEvents.is_movement_input():
		transition.emit("walk")
	if player.current_tool == DataTypes.Tools.Axewood and GameInputEvents.use_tool():
		transition.emit("chopping")
	if  player.current_tool == DataTypes.Tools.TillGround and GameInputEvents.use_tool():
		transition.emit("tilling")
	if player.current_tool == DataTypes.Tools.WaterCrops and GameInputEvents.use_tool():
		transition.emit("watering")
func _on_enter() -> void:
	pass


func _on_exit() -> void:
	animated_sprite_2d.stop()
