    if (isinstance(world.current_id, list)):
        world.current_id = world.current_id[0]
    message = []
    neighbors = []
    world.sub_tree_length = int (world.sub_tree_length)
    for neighbor in world.neighbors : 
        neighbors.append(int(neighbor))
    src = int(src)
    log(f"current id {world.current_id}{type (world.current_id)}, current parent {world.current_parent}{type (world.current_parent)}, current status {world.current_status}{type (world.current_status)}, current round {world.current_round}{type (world.current_round)}")
    for c in msg : 
        if (c == 'e') : 
            id = -1 
            for c in msg : 
                if c.isdigit() :
                    id = c 
            for neighbor in (world.neighbors) :
                world.send_message(to = neighbor, msg = 'e' + f'{id}')
            print(f'final leader is {id}', file=sys.stdout)
            sys.exit()
        elif c.isdigit() :
            message.append(int(c))

    # log the receiving message        
    log(f"processed message is {message} and is from {src}")

    # if the incoming wave is better 
    if (message[0] > world.current_round) or (message[0] == world.current_round and message[1] > world.current_id) :
        world.current_status = False
        # change to the incoming wave 
        world.current_parent = src
        # clear list of the neighbors returning the message 
        returned_msgs_in_round.clear()
        world.current_round = int(message[0])
        world.current_id = int(message[1])
        world.sub_tree_length = 0 
        # send message to all neighbors except parent 
        for neighbor in (world.neighbors) :
            if (neighbor != str(world.current_parent)):
                world.send_message(to = neighbor, msg = msg)
    # same round and same id
    elif (message[0] == world.current_round and message[1] == world.current_id ) : 
        # append sender to the list of neighbors returning the message 
        if not (src in returned_msgs_in_round) :
            returned_msgs_in_round.append(src)

        if len(message) > 2: 
            log(f'returned subtree is {message[2]}')
            if (src != world.current_node):
                world.sub_tree_length += int(message[2]) + 1 
        log(f"sub tree is {world.sub_tree_length}")
        log(f"received from {returned_msgs_in_round}")
        temp_neighbors = neighbors
        # remove parent from the list of neighbors 
        if (world.current_parent in temp_neighbors) :
            temp_neighbors.remove(world.current_parent)
        if (set(returned_msgs_in_round) == set(neighbors)) and (world.current_status) :
            # if an active node has received message from all it's children 
            log("finished round")
            print(f'leader in round {world.current_round} is {world.current_node}', file=sys.stdout)
            print(f'subtree length {world.sub_tree_length}', file=sys.stdout)
            # select a new id for the next round 
            world.current_id = random.sample(range(world.network_number_of_nodes), 1)
            world.current_round = world.current_round +1 
            # if the subtree doesn't consists of the whole tree then we shall start a new round 
            if (world.sub_tree_length + 1  < world.network_number_of_nodes) : 
                world.subtree_length = 0 
                for neighbor in (world.neighbors) :
                    world.send_message(to = neighbor, msg = [world.current_round , world.current_id])
            else :
            # the leader broadcasts it's id as the leader and exits 
                print(f'final leader is {world.current_node}', file=sys.stdout)
                for neighbor in (world.neighbors) :
                    world.send_message(to = neighbor, msg = ["e" , world.current_id])
                sys.exit()
        # if a passive node has received message from all neighbors, 
        #   returns the message to it's parent 
        elif (set(returned_msgs_in_round) == set(temp_neighbors)) :
            print(f'parent is {world.current_parent} and the subtree length is {world.sub_tree_length}', file= sys.stdout)
            world.send_message(to = str(world.current_parent), msg = msg + f'{world.sub_tree_length}') 
   