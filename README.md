Todo:

- Text dirty render
- modify body to include multiple shapes?
- body sprite remove sprite inheritance
- Research layered groups, organize sprite groups
- blocks are sliding off and difference in weights is not noticeable
  - already cancelling out deck and block angle and angle velocity, but there is a small amount that is enough to continue
  - ideas for how to prevent this
    - block velocity: cancel sideways velocity
    - new seesaw idea
    - add a duplicate seesaw above, attached with set distance to the edges of the deck
- loading blocks cannot have more than one block in it

- Seesaw detects greater than, less than, and equal to 
  - blocks are slipping off
  - add Block only collides with top of deck
  
- Pivot joint on mouse as it picks up block?
- Why are the joints created as sprites?
- Communication between level attributes (weight, blocks) and objects
~~- Blocks stay as kinematic if you move the mouse too fast when unclicking~~

Functional but can be optimized
- Find consistent method for handling the stupid pymunk flipped coordinates system
- make sprite groups for collisions/filtering
- make collision type dictionary