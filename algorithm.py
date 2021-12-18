import sys
import random
from typing_extensions import Self
from networkx.classes.function import neighbors

from networkx.generators.random_graphs import watts_strogatz_graph
from networkx.readwrite.pajek import write_pajek
from world import log, world
returned_msgs_in_round = []


def process_msg(src, msg):
    #  process the received message 
    message = []
    # error handeling 
    if isinstance(world.current_id, list) : 
        world.current_id = world.current_id[0]
    if isinstance(world.current_round, list) : 
        world.current_round = world.current_round[0]
    # on leader election end the leader broadcasts exit to the network 
    #   , along with it's id as the leader 
    if msg == 'exit' : 
        print(f'leader is {world.current_id} ', file= sys.stdout)
        for neighbor in world.neighbors : 
            world.send_message( neighbor, 'exit')
        sys.exit()
    # converting string msg into integer 
    for char in msg : 
        if char.isdigit():
            message.append(int(char))
    sub = 0 
    if (len(message) == 3 ) :
        sub = message[2]
    elif (len(message) > 3) : 
        for i in range(2, len(message)) : 
            sub += message[i] * 10 **(len(message)-1 - i)
    neighbors = world.neighbors 
    temp_neighbors = neighbors 
    log(f'message is {msg}')
    log(f'this node\'s round : {world.current_round}, id : {world.current_id}, parent :{world.current_parent}, status :{world.current_status}')
    log(f'the received message is, round {message[0]}, id : {message[1]}, sub_tree: {sub }, from {src}')
    if (message[0]> world.current_round) or (message[0] == world.current_round and message[1] > world.current_id) :
        #  change to the received wave 
        world.current_parent = src
        world.current_round = message[0] 
        world.current_id = message[1]
        world.current_status = False 
        returned_msgs_in_round.clear()
        world.sub_tree_length = 0 
        log(f'changed wave to {world.current_id}')
        #  according to echo algortihm, when joining a wave a node must send 
        #       the received wave's message to it's neighbor except for the parent 
        for neighbor in neighbors : 
            if  neighbor != src : 
                world.send_message( neighbor, [message[0], message[1], 0])

    elif (message[0] == world.current_round) and (message[1] == world.current_id) :
        if not src in returned_msgs_in_round and src != world.current_parent : 
            if src != world.current_node :
                #  adding returned sub_tree of child into the parent's sub_tree
                world.sub_tree_length += sub 
                #  adding child to the sub_tree
                world.sub_tree_length += 1 
            returned_msgs_in_round.append(src)
        log(f'received message from {returned_msgs_in_round}')
        print(f'this nodes subtree is {world.sub_tree_length} latest update came from {src} and was {sub}', file = sys.stdout)
        if (world.current_parent in temp_neighbors) :
            temp_neighbors.remove(world.current_parent)
        log(f'neighbors {temp_neighbors}')
        #  according to echo's algorithm when the submitted wave's messages return from all neighbors a node must 
        #   a) send the message to it's parrent if it's not an initiator 
        #   b) decide if it's an initiator 
        if (set(returned_msgs_in_round) == set(temp_neighbors)) :
            log("returned from all of the neighbors ")
            if (world.current_status) : 
                if (world.sub_tree_length + 1 >= world.network_number_of_nodes) : 
                    #  if the node's sub_tree length is the same as the network size, 
                    #       all nodes have received it's wave and joined it. 
                    #  since all nodes have joined the wave, all the network accept this node as the leader
                    print(f' final leader is me {world.current_node} with the winning id as {world.current_id}', file= sys.stdout) 
                    print(f'sub tree length is {world.sub_tree_length}')
                    for neighbor in neighbors :
                        world.send_message(neighbor, "exit")
                    sys.exit()
                else : 
                    #  if sub_tree length is less than the network size another round of the algorithm must begin
                    world.current_round +=  1 
                    world.sub_tree_length = 0 
                    world.current_id = random.sample(range(world.network_number_of_nodes), 1)
                    returned_msgs_in_round.clear()
                    for neighbor in neighbors : 
                        world.send_message( neighbor, [world.current_round, world.current_id, 0])
            else : 
                #     a node that's not an initiator must return the message to it's parent when received from all neighbors
                print(f'returning to parent {world.current_parent}, the id is {world.current_id} and the sub tree length is {world.sub_tree_length}')
                world.send_message(world.current_parent, [world.current_round, world.current_id, world.sub_tree_length])
