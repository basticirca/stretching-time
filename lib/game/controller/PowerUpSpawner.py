#!/usr/bin/python
# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import random

from lib.game.controller.Spawner import Spawner
from lib.game.spawn.Coin import Coin

class PowerUpSpawner(Spawner):
	''' Manages creation of spawn objects and power ups collectable.
		Also observes position of spawn. If spawn exceeds max bounds,
		it will be removed by the spawner. '''

	def __init__(self):
		self.super(PowerUpSpawner).__init__()

		# vanishing position for spawned objects
		# objects exceeding this plane will be deleted by spawner
		self.z_vanish = 0

		self.max_auto_spawns = 1

		# stores metadata for spawn types
		# format (name, file_path, blocked)
		self._spawn_type_info = {
			0 : ['bomb', 'data/textures/powerups/bomb/bomb_coin_white.png', False],
			1 : ['cup_decrease', 'data/textures/powerups/cupcakes_decrease/cupcakes_decrease_white.png', False],
			2 : ['cup_increase', 'data/textures/powerups/cupcakes_increase/cupcakes_increase_white.png', False],
			3 : ['freeze', 'data/textures/powerups/freeze/freeze_coin_white.png', False],
			4 : ['god', 'data/textures/powerups/godmode/godmode_coin_white.png', False],
			5 : ['life', 'data/textures/powerups/life/life_coin_white.png', True],
			6 : ['normaltime', 'data/textures/powerups/normaltime/normaltime_coin_white.png', False],
			7 : ['repair', 'data/textures/powerups/repair/repair_coin_white.png', True],
			8 : ['twice', 'data/textures/powerups/twice/twice_coin_white.png', False]
		}

		self._spawn_string_to_type = {
			'bomb' : 0,		
			'cup_decrease' : 1,		
			'cup_increase' : 2,		
			'freeze' : 3,		
			'god' : 4,		
			'life' : 5,		
			'normaltime' : 6,		
			'repair' : 7,		
			'twice' : 8
		}

	def my_constructor(self, PARENT_NODE = None, AUTO_SPAWN = True, Z_VANISH = 0):
		self.super(PowerUpSpawner).my_constructor(PARENT_NODE, AUTO_SPAWN)

		self.z_vanish = Z_VANISH

	def spawn(self, SPAWN_MIN = avango.gua.Vec3(), SPAWN_MAX = avango.gua.Vec3(), SPAWN_TYPE = 0):
		''' Spawns random spawn at random location. '''
		x = random.uniform(SPAWN_MIN.x, SPAWN_MAX.x)
		y = random.uniform(SPAWN_MIN.y, SPAWN_MAX.y)
		z = random.uniform(SPAWN_MIN.z, SPAWN_MAX.z)

		m = avango.gua.make_trans_mat(x, y, z)

		spawn = Coin()
		spawn.pickable = self.spawn_pickable

		tex = ''
		if SPAWN_TYPE in self._spawn_type_info and not self._spawn_type_info[SPAWN_TYPE][2]:
			tex = self._spawn_type_info[SPAWN_TYPE][1]
			spawn.flags.append(self._spawn_type_info[SPAWN_TYPE][0])
		
		spawn.my_constructor(
			PARENT_NODE = self.spawn_root,
			SPAWN_TRANSFORM = m,
			TEXTURE_PATH=tex
		)
		
		spawn.movement_speed = random.uniform(0.05, 0.15)
		spawn.rotation_speed = 2.0
		spawn.rotation_axis.x = 0.0
		spawn.rotation_axis.y = 1.0
		spawn.rotation_axis.z = 0.0
		spawn.rotation_axis.normalize()
		spawn.setScale(self.spawn_scale)

		self.spawns_dict[spawn.game_object_id] = spawn

	def _remove_vanished(self):
		''' Removes objects moved out of application bounds. '''
		kill_list = []
		for spawn_id in self.spawns_dict:
			spawn = self.spawns_dict[spawn_id]
			z = spawn.bounding_geometry.WorldTransform.value.get_translate().z
			if z > self.z_vanish:
				kill_list.append(spawn_id)

		if len(kill_list) > 0: 
			self.remove_spawns(kill_list)

	def set_spawn_type_block(self, TYPE_NAME, STATE):
		''' changes block of objects of given TYPE_NAME from being spawned. ''' 
		if TYPE_NAME not in self._spawn_string_to_type:
			return
		spawn_type = self._spawn_string_to_type[TYPE_NAME]
		self._spawn_type_info[spawn_type][2] = STATE

	def get_spawn_type_block(self, TYPE_NAME):
		''' foo bar baz. FOR jo GG EZ PIIIEUFJHG. '''
		if TYPE_NAME not in self._spawn_string_to_type:
			return None
		spawn_type = self._spawn_string_to_type[TYPE_NAME]
		return self._spawn_type_info[spawn_type][2]
			
	def _auto_spawn(self):
		''' Spawns one random object inside configured spawn bounds,
			if number of total spawned objects < self.max_auto_spawns. '''
		all_blocked = True
		for spawn_type in self._spawn_type_info:
			if not self._spawn_type_info[spawn_type][2]:
				all_blocked = False
				break

		if self.spawn_count() < self.max_auto_spawns and not all_blocked:
			spawn_type = random.randint(0, 8)
			while self._spawn_type_info[spawn_type][2]:
				spawn_type = random.randint(0, 8)
			self.spawn(self.auto_spawn_min_pos, self.auto_spawn_max_pos, spawn_type)