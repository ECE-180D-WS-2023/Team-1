# points need to be decremented by Note also since needs to check when notes fall out of map
# points need to be kept in game too, put here to avoid circular dependency
points = 0

# probably put global flag for imu actions here too so the on_message can modify it and then have the game read it