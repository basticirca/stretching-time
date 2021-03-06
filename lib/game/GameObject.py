import avango
import avango.gua
import avango.script

from avango.script import field_has_changed
import time

class GameObject(avango.script.Script):
    ''' Defines base interface for all visualizable objects in the game. '''

    instance_count = 0
    sf_destroyed = avango.SFBool()
    sf_active = avango.SFBool()

    def __init__(self):
        self.super(GameObject).__init__()

        # used as a transmitter to let connected fields know when a GameObject is destroyed
        self.sf_destroyed.value = False

        # stores an avango.gua.nodes.TrimeshNode to visualize instance 
        self.bounding_geometry = None
        
        # stores a reference id to this instance
        self.game_object_id = GameObject.instance_count

        # flag denotng whether this instance is active or not
        self.sf_active.value = True

        GameObject.instance_count += 1

        # flag stating whether the object has just been spawned
        # solves bug of intersecting just spawned objects,
        # which do not have their transformation applied yet
        self._just_spawned = True 

        # flag stating whether this instance can trigger collision
        self.can_trigger_collision = True

        # stores creation time
        self._creation_time = time.time()

        self.always_evaluate(True)

    def evaluate(self):
        ''' Frame based update function. '''
        if self._just_spawned:
            self._just_spawned = False

    def cleanup(self):
        ''' cleans up pending connections into the application, so that object can be deleted. '''
        self.always_evaluate(False)
        self.sf_destroyed.value = True
        self.sf_destroyed.disconnect()
        if self.bounding_geometry != None:
            self.bounding_geometry.Parent.value.Children.value.remove(self.bounding_geometry)

    def hide(self):
        ''' hides this gameobject. '''
        self.bounding_geometry.Tags.value = ['invisible']

    def show(self):
        ''' makes the geometry visible. '''
        self.bounding_geometry.Tags.value = []

    def set_active(self, ACTIVE):
        self.sf_active.value = ACTIVE

    def get_active(self):
        return self.sf_active.value

    def get_creation_time(self):
        return self._creation_time

    def _on_active_changed(self):
        if self.bounding_geometry == None:
            return
            
        if self.get_active():
            self.show()
        else:
            self.hide()

    def get_just_spawned(self):
        ''' getter for self._just_spawned. '''
        return self._just_spawned 

    def get_bounding_box(self):
        ''' returns the bounding box of the game object bounding_geometry. '''
        return self.bounding_geometry.BoundingBox.value

    def is_collision_trigger(self):
        ''' returns true if can_trigger_collision == True,
            and self._just_spawned == False. '''
        return self.can_trigger_collision and not self._just_spawned

    def intersects(self, BOUNDING_BOX):
        ''' Checks if given bounding box intersects 
            the player geometries bounding box. '''
        return self.get_bounding_box().intersects(BOUNDING_BOX)

    def get_num_game_objects(self):
        return GameObject.instance_count

    @field_has_changed(sf_active)
    def sf_active_changed(self):
        self._on_active_changed()

