# EchoAlgorithmWithExtinction
Distributed Systems Course Project
## Introduction 
In this project we are to implement and test the Echo leader election algorithm with extinction. This is a Las Vegas distributed algorithm, meaning it will end with the probability one but the configuration may be wrong. In the following sections of this report we will further discuss the algorithm, the implementation the result and a brief analysis of the message complexity of this algorithm using the execution results of our own code. 
## Implementation 
### Algorithm 
The algorithm starts with a state where one or multiple nodes initiate a leader election algorithm. 
Initiators start the algorithm by sending a message containing round, id, and sub-tree length. At first, each initiator randomly selects an id within the range of the number of the nodes in the network and sends out the message with round and sub-tree set to zero. 
At each round a node receiving message acts as below: 


<img width="780" alt="image" src="https://user-images.githubusercontent.com/43328710/175038317-e2ef1ce6-d9c4-4ac6-9eef-85493a7ce509.png">

### Code 
This algorithm is implemented with the help of runner code provided with the project description.The runner code runs multiple nodes with the help of python multi-thread processing. Nodes are connected to each other with weighted edges which may or may not have packet loss or delay.
Each node is implemented by node.py, and runs until end of the algorithm. Nodes communicate with the help of *rabbitmq*[1] library in python. 
On every received message, perocess\hyph{msg} function is called to handle the message according to the algorithm. 
Initially each node's id, round, parent, status, sub-tree length are set to {-1, 0, -1, False, 0}. Initial set-up is done at *initiate* function. 

When receiving a message we act on two conditions, whether it's a new message with higher round/id or the message is a returning message from neighbors. In the first condition we change to this wave as referred in the block of code below. By changing the wave, the current node's id becomes the new wave's id and it's parent will be the sender of the message also if the node is still active it becomes passive by changing it's status to *False*. The variable returned *messages-in-round* keeps record of the messages with the same id and round received by the current node. Since this node has recently changed to the new wave this variable must be set to *empty*. On the other hand if a node has only one neighbor which will be it's parent, it must immediately return the received message to it's parent since no other node is left to send the message to.
                        
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

If the incoming message has the same id and round as the current node then it must wait until receipt of the message from all the neighbors. When the current node has received message from all neighbors, if passive, the current node returns the message along with it's sub-tree length to it's parent according to lines 101-104 of the code block below.
If the current node is still active, it acts according to the length of it's sub-tree. The sub-tree of this node shows how many other nodes took part in it's wave. If the whole network took part in it's wave then all other nodes are passive and this node is the leader. If the sub-tree includes the whole network the current node broadcast a message with it's id and *exit* to the network and announces itself as the leader.


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
 
 ## Performance Analysis of the Algorithm
 In this section we have generated random graphs using *networkx* library with different topologies to analyze the performance of the algorithm on each of them. As referred to in [2] message complexity of this algorithm is $O(E)}$. Since each message in a round is sent twice in each edge and we have finite number of rounds. Here we will test this claim with the results we got from the implementation. 
 ### Output on Rings
 
 Each ring with \(N\) nodes has \(N\) edges. With the help of networkx generator function, several rings with different number of nodes was generated. The number of messages communicated in each graph, was plotted in figure below as a function of the edges of the graph.
 
 <img width="517" alt="image" src="https://user-images.githubusercontent.com/43328710/175049188-5bb9e4b8-f98b-4f41-ae4f-637bfc4c81fc.png">

### Output on Random Trees 

Each tree with \(N\) nodes has \(N-1\) edges. Here several random trees were generated and testes, the result can be seen from figure\ref{fig:plotOfRandomTrees} as plotted. The x axis is the number of the edges of the tree and y axis shows the number of messages communicates until deciding the leader. 

<img width="569" alt="image" src="https://user-images.githubusercontent.com/43328710/175049818-7d0e015d-47fe-4e60-a9e2-74832e377971.png">


### Output on Complete Graphs
A complete graph of \(N\) nodes has \(\frac{N \times (N-1)} {2} \) edges total. Figure below shows the number of messages as the number of edges on the graph increases.

<img width="569" alt="image" src="https://user-images.githubusercontent.com/43328710/175049883-c9f51065-f872-49d9-903f-cb2c973362b4.png">

## References
<a id="1">[1]</a> 
https://www.rabbitmq.com/

<a id="2">[2]</a> 
W. Fokkink,
Distributed algorithms: an intuitive approach. 2018.
