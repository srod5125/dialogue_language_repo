import networkx as nx
from lark import Lark


class DialogueLang():
    def __init__(self, text):
        self.text = text
        self.parser = Lark(r"""
            ?start : tag+

            ?tag : "<<" var ">>" "{" (exchange_blocks|function_def)* "}"

            ?exchange_blocks : "<" "base" ">" "{" statement* "}" -> start_dialogue
                            | "<" "receive" var ["in" state] ">" "{" statement* "}" -> receive_msg
                            | "<" "init" ">" "{" statement* "}" -> graphval_init
                            | "<" "on_tick" ">" "{" statement* "}" -> update
                            | ">" var "route" ["in" state] "<" "{" statement* "}" -> msg_router
                            | ">" var "init" "<" "{" statement* "}" -> msg_init
            
            ?function_def : "func" var "(" [var ("," var)*] ")" "{" statement* "}"


            ?statement : "for" (name "=" arithmatic_expr) "to" conditional_expr "{" statement+ "}" -> for_loop
                        | "forall" name "as" var "{" statement+ "}" -> for_each_loop
                        | "while" "(" conditional_expr ")" "{" statement+ "}" -> while_loop
                        | "if" "(" conditional_expr ")" "{" statement+ "}" [( "else" "{" statement+ "}"  )+] -> if_statement
                        | assignment ";"
                        | "send" name ";" -> send
                        | "return" expr ";" -> return
                        | "log" expr ";" -> text_log
                        | directive
                        | function_call ";"
            
            ?directive : "on" ":" "arrive" "{" statement+ "}" -> arrive_directive
                        | "on" ":" "enroute" "{" statement+ "}" -> enroute_directive
                        | "on" ":" "depart" "{" statement+ "}" -> depart_directive
                        | "on" ":" var "{" statement+ "}" -> defined_directive

            ?assignment : name "=" expr -> assign
                        | name "=" atom
                        | name "=" SINGLE_QUOTED_STRING
                        | name "=" conditional_expr "?" (atom|expr) ":" (atom|expr) -> ternary
                        | name "+=" arithmatic_expr -> plus_equal
                        | name "-=" arithmatic_expr -> minus_equal
                        | name "=" "msg"
            
            ?expr : conditional_expr | arithmatic_expr | string_manipulation_expr | function_call

            ?function_call : var "(" [expr ("," expr)* ] ")"
                            | "len" "(" (list|name) ")" -> list_len
                            | "rand" "(" (SIGNED_NUMBER | name | dict | list) ")" -> random_val
                            | "insert" "(" name "," expr "," arithmatic_expr ")" -> insert_list
                            | "remove" "(" name "," expr "," arithmatic_expr ")" -> insert_list
                            | "in" "(" name "," expr ")" -> is_in
                            | "waitUntil" "(" conditional_expr ")"  -> wait_until

            
            ?conditional_expr : conditional_expr "&" rest_cond -> and_condition
                                | conditional_expr "|" rest_cond -> or_condition
                                | "!" rest_cond -> not_condition
                                | (conditional_expr "==" rest_cond | arithmatic_expr "==" arithmatic_expr ) -> equal_condition
                                | (conditional_expr "!=" rest_cond | arithmatic_expr "!=" arithmatic_expr ) -> unequal_condition
                                | "(" conditional_expr ")"
                                | conditional_expr ">>" rest_cond -> greater_than
                                | conditional_expr "<<" rest_cond -> less_than
                                | rest_cond
            ?rest_cond : expr | bool 
<<<<<<< HEAD
            ?bool : "true"->true| "false"->false
=======
            ?bool : "true" -> true | "false" -> false 
>>>>>>> b4f747dc9ab841e949b3d4cf720fa4ab4fb6cc3b

            ?arithmatic_expr : "(" arithmatic_expr ")"
                                | arithmatic_expr "-" rest_aritmatic -> sub
                                | arithmatic_expr "*" rest_aritmatic -> mul
                                | arithmatic_expr "/" rest_aritmatic -> div
                                | arithmatic_expr "+" rest_aritmatic -> add 
                                | rest_aritmatic
            ?rest_aritmatic : arithmatic_expr | SIGNED_NUMBER | name 
                                 | "delta_t" -> tick | "total_t" -> total_tick | math_funcs | function_call

            ?math_funcs : "sin" "(" arithmatic_expr ")" -> sin_function
                            | "cos" "(" arithmatic_expr ")" -> cos_function

            ?string_manipulation_expr : string_manipulation_expr "+" rest_string -> string_add
                                        | rest_string
            ?rest_string : string_manipulation_expr | SINGLE_QUOTED_STRING | name 


            ?name:  var | property | dict_value | list_val | node_val | msg_val
            ?var: WORD | CNAME
            ?dict_value : var "[" (arithmatic_expr|name|string_manipulation_expr)  "]" -> dict_access
            ?list_val : var "[" (arithmatic_expr)  "]" -> list_access
            ?property: name "->" var -> property_var
                        | name "->" "data" ["[" (arithmatic_expr|name|string_manipulation_expr)  "]"] -> msg_data
                        | name "->" "sender" -> msg_sender
                        | name "->" "journey" "[" (arithmatic_expr)  "]" -> msg_journey
                        | name "->" "rate" -> msg_rate
                        | name "->" "destination" -> msg_destination

            ?dict : "{" [ (SIGNED_NUMBER|SINGLE_QUOTED_STRING|name) ":" (name|atom) ( "," (SIGNED_NUMBER|SINGLE_QUOTED_STRING|name) ":" (name|atom) )* ] "}"
                    | | "{" (name|list) "as" var ";" [ conditional_expr ] ";" [ (lamda|var) ]  "}" -> dict_comprehension
            ?list : "[" [   (name|atom) ( "," (name|atom) )*    ] "]"
                    | "[" (name|list) "as" var ";" [ conditional_expr ] ";" [ (lamda|var) ]  "]" -> list_comprehension
            ?lamda : var ["," var] ":" expr -> lambda_expr

            ?node_val : "@" "queue_size" -> queue_len
                        | "@" "queue" -> node_queue
                        | "@" "state" -> node_status
                        | "@" "neighbors" -> node_neighbors         
                        | "@" "edges" [("->" var|"->" "to")] -> node_edges
                        | "@" "id"-> node_id
                        | "@" (var | dict_value | list_val)  -> node_access

            ?msg_val : "#" (var | dict_value | list_val) -> msg2_access
                        | "#" "state" -> msg2_status
                        | "#" "rate" -> msg2_rate 
                        | "#" "destination" -> msg2_destination
                        | "#" "sender" -> msg2_sender
                        | "#" "path" ["->" var] -> msg_path
                        | "#" "journey" "[" (arithmatic_expr)  "]" -> msg2_journey
                        | "#" "data" ["[" (arithmatic_expr|name|string_manipulation_expr)  "]"] -> msg2_data
            
            ?state : var|SIGNED_NUMBER [("." (var|SIGNED_NUMBER))*]
            ?atom : SIGNED_NUMBER | SINGLE_QUOTED_STRING | bool| dict |list
            SINGLE_QUOTED_STRING  : /'[^']*'/

            _seq{val}: val ("," val)* 

            %import common.WORD
            %import common.CNAME
            %import common.SIGNED_NUMBER
            %import common.WS
            %import common.C_COMMENT

            %ignore WS
            %ignore C_COMMENT
            """, start='start')


# --------TO_DO--------

# access edge data from node, or edge as message

# output, user input
# processing received messages
# movie controls for recording and timing recordings of data: clock = 0.1, record 5-19s
# importing graph types, initializing graphs via json
# wrappers for showcasing on matplot lib
# adding function capacity
# define graph, init graph, import common graph
# print output, using pandas to log data https://www.youtube.com/watch?v=dcqPhpY7tWk

# where and how messages travel, the throw specifies how a message travels
# neighbor memory access
# prevent batch processing from happening in a throw block

# if no start state is supplied, defaults to start

# implmementing neigbor broadcasting only, throw msg => catch msg -> send msg format
#                                   sends the same message
#                                    path variable is updated with current state and
#                                   id of node traversed

# block access to sender by saying if response->state != somestate, msg always includes state and id of caught msg
#
# queue batch processing model for catches, yeild processing or conditional queue breaks and plays
# enforce message case sensitivity

# message control sequence starts in depart

# interfacing two protocls
# state manager interface

# break in loop

# description of random: if list of size 2 is supplied, that is accepted as range
#                          for greater size, an element is randomly chosen,

# two types of allowed graph are undirected and directed

# stronger from message perspective implmentation

# start, instead of throw, replace send with throw, add @Node,#Edges for global acesss
# need acess to global information
# how to write from message perpective: directives are threadblocking
# directives
# timing, total time vs pinging time
# clarify edge acess vs message property acesss message property values
# loops automatically if not stopped

"""
-- tcp 
-- game of life x
-- busses in city quantamag node x,msg x
-- charged particles
-- harvard bot 
-- boolean circuit x
-- kuromato model y strogatx fireflies
-- ant colony optimization x
-- sudoku wave propogation
-- bee voting
"""

if __name__ == '__main__':
    data = """
            <<XYZ>>
            {
                >a route<
                {

                }
            }
            """
    d_lang = DialogueLang(data)
    print(d_lang.parser.parse(data).pretty())

# ----------------------------------------------------
# game of life
"""

<base> 
{
    request = msg;
    send request;
}
<receive request>
{
    response->data = {'state':@state};
    send response ;
}
<receive response>
{
    waitUntil(@queue_size == 4)
    {
        forall @queue as r
        {
            if (r->data['state'] == 'ALIVE')
            {
                sum += 1;
            }
        }

        if ( @state == 'ALIVE' )
        {
            @state = sum == 2 | sum == 3 ? 'ALIVE' : 'DEAD';
        }
        else
        {
            @state = sum == 3 ? 'ALIVE' : 'DEAD';
        }

        @state = base;
    }
}
"""
# ----------------------------------------------------
"""
> ant enroute in state <
{
    lay down pheremone as you back track after you found food
    then wander again, but with weighted pheremone trail as guide
}
> ant depart <
{
    forall edges:
        give weigted probabolites to travel along edges,
        higher weight for more pheremenone
        randomly select edge based on weights
}


until node != goal or timeout reached:
    choose new destination weighted by pheremone and if node has not been visited
    if goal found:
        backtrack along visited routes and drop pheremone
        repeat

randomwalk ant
    while node != goal or timeout reached
        random-selection
        on:arrive{if @state==goal; backtrack}
backtrack ant
    for i in visited:
        if i->state = 'start'
            #state = randomwalkwithpheremone
        ant-destination = i
        on:enroute{
            $pheremenone += 1
        }
randomwalkwithpheremone ant
    while node != goal or timeout reached
        random-selection with pheremeones
        on:arrive{if @state==goal; backtrack}
    

"""

# -------------
# quanta mag busses, node perspective

"""
bus sends spy to random destination or along route
when spy arrives, spy grabs infromation and returns
bus determines acceleration based of spy info, or arrival bus resets accelerationd
bus departs to where spy was, repeat
"""


"""
<base>
{
    spy = msg;
    spy->destination = rand[@neigbors];
    spy->rate = 0.5*delta_t;
    send spy;
}
<receive spy>
{
    spy->data = {'pass_count':passengar_count};
    send spy;
    @state = move_bus;
}
<receive spy in move_bus>
{
    if (spy->data[['pass_count']] >> 10)
    {
        bus->rate += 0.1;
    }
    else
    {
        bus->rate -= 0.1;
    }
    send bus;
}
<receive bus>
{
    bus->rate = 1;
    @state = base;
}
"""
# ------------------------
# quanta mag busses msg perpective
"""

<< Quanta_Magazine_Busses >>
{
    <on_tick>
    {
        if (rand[[0,1]]>>0.5)
        {
            @passengar_count += 1;
        }
    }
    >spy init<
    {
        #rate = 0.5*delta_t;
    }
    >spy depart<
    {
        #destination = rand(@neigbors);
    }
    >spy arrive<
    {
        #data = @passengar_count;
        /*field propery, pasengar count, belongs to node*/

        #destination = #sender;
        send @spy;
        #state = 'got_info';
        /*note the syntax, the spy is not sending itself, 
        instead it is accessing the node to send itself*/
    }
    >spy arrive in got_info<
    {
        #state = 'came_back';
    }
    >bus init<
    {
        #capacity = 5;
    }
    >bus depart<
    {
        /*
            send spy to random node or given path
            wait until spy arrives
            if spy say lots of people are there go fast,
            else go slow
        */

        send @spy;

        waitUntil(@spy->state == 'came_back');
        
        #rate = @spy_count >> 10 ? 1 : -1;
        #destination = @spy->destination;

        @spy->state = 'spy_again';
        
    }
    >bus arrive<
    {
        #rate = 1;
        @passengar_count -= #capacity;
        send @bus;
    }
}
"""
# ------------------------

# ?batchprocessing : "valve" "(" [initialization] ";" [conditional_expr] ";" [update] ")" "{" statement+ "}" -> batch_process


""" 
<< Univerality_Busses >>
{
    >bus route<
    {
        send @spy;
        waitUntil(@spy->returned);

        /*arbitrary passengar threshold*/
        if(@spy->passengar_count >> 6)
        {
            #rate += 0.2;
        }
        else
        {
            #rate -= 0.2;
        }
        #destination = @spy->visited;
        send @bus;

        on:arrive
        {
            #rate = 1;
        }
    }
    >spy route in going<
    {
        on:depart
        {
            #returned = false;
            #prev = @id;
            #destination = random(@neighbors);
        }
        on:arrive
        {
            #passengar_count = @passengar_count;
            #state = 'comeingback';
            #destination = #prev;
            #next = @id;
            send @spy;
        }
    }
    >spy route in comeingback<
    {
        on:arrive
        {
            #returned = true;
            #destination = #next;
            send @spy;
            /*so the spy follows the bus*/
        }
    }
}

"""


# ?iter_expr : (list_val|name) iter_function*
# ?iter_function : ":>"  "map" "(" (var|lamda) ")" -> map
# | ":>" "filter" "(" (var|lamda) ")" -> filter
# | ":>" "reduce" "(" (var|lamda) ")" -> reduce


# logically incorrect?
"""
<< Ant_Optimization >>
{
    > ant arrive<
    {
        if(@state == 'goal')
        {
            #state = 'lay_ph';
        }
        send @ant;
    }
    > ant depart<
    {
        #destination = rand(@neighbors);
    }
    > ant depart in lay_ph<
    {
        sum = 0;

        forall @edges as e
        {
            /*give weigted probabolites to travel along edges*/
            sum += e->pheromone;
        }

        if (sum == 0)
        {
            #destination = rand(@neighbors);
        }
        else
        {
            /*encrourage a tiny fraction of messages to still choose randomly at a 10percent level */
            availablePaths = [ @edges as e; e->pheromone == 0; e=e->pheromone+0.1 ];

            forall availablePaths as e
            {
                if (e->pheromone/sum  >> rand([0,1]) )
                {
                    #destination = e->to;
                }
            }
        }
    }
    > ant enroute<
    {
        #path->pheromone += 1;
    }
    <init>
    {
        #pheromone = 0;
    }
    <on_tick>
    {
        if(#pheromone >> 0)
        {
            #pheromone -= 0.2;
        }
    }
}
"""


"""

<< Ant_Optimization >>
{
    /*ant finds goal, traces pheremone over goal, 
    when going again pheremone is just weighted probability*/

    /*destination cant be in journey,how to back track over route*/
    >ant init<
    {
        #state = 'search';
        #no_backtrack = true;
    }
    > ant arrive <
    {
        if(@state == 'goal')
        {
            #state = 'go_back';
            
            #pathLenFromStart = len(#journey);
            #count = 1;
        }
        if(@state == 'base' & #state == 'go_back')
        {
            #state = 'search';
        }
        send @ant;
    }
    > ant depart<
    {
        #destination = rand(@neighbors);
    }
    > ant depart in go_back<
    {
        /*needlessly complicated*/
        #destination = #journey[#pathLenFromStart - #count];
        #count+=1;
    }
    > ant depart in search<
    {
        sum = 0;

        forall @edges as e
        {
            /*give weigted probabolites to travel along edges*/
            sum += e->pheromone;
        }

        if (sum == 0)
        {
            /*go back through journey*/
            #destination = #journey[-1];
        }
        else
        {
            /*new list is copy of previous one with changes*/
            pathsWithPheremone = [ @edges as e; e->pheromone == 0; e:e->pheromone+0.1 ];

            forall pathsWithPheremone as e
            {
                if (e->pheromone/sum  >> rand([0,1]) )
                {
                    #destination = e->to;
                }
            }
        }
    }
    > ant enroute in lay_ph<
    {
        #path->pheromone += 1;
    }
    <init>
    {
        #pheromone = 0;
    }
    <on_tick>
    {
        if(#pheromone >> 0)
        {
            #pheromone -= 0.2;
        }
    }
    func len(list)
    {
        count = 0;
        forall list as l
        {
            count += 1;
        }
        return count;
    }
}


"""
# revised
"""
<< Ant_Colony_Optimization >>
{
    > ant route in randomwalk <
    {
        timeout = 10;
        count = 0;

        #visited = [];

        while(timeout-count>>0 )
        {
            next = rand(@neighbors);
            while (! in(#visited,next) )
            {
                next = rand(@neighbors);
            }

            add(#visited,next,len(#visited)-1);
            #destination = next;
                
                /*this directive will trigger on arrival*/
                on:arrive 
                {
                if(@state == 'goal')
                {
                    #state = backtrackwithpheremone;
                }
                send @ant;
                }

            count += delta_t;
        }
    }
    >ant route in backtrackwithpheremone<
    {
        /*using the visited as a history*/
        itr = len(#visited)-2; /*get previously visited node, not current*/
        while(itr>>0)
        {
            #destination = #visited[itr];
            itr-=1;
        }
        on:arrive
        {
            if(@state == 'start')
            {
                #state = randomwalkwithpheremone;
            }
            send @ant;
        }
    }
    >ant route in randomwalkwithpheremone<
    {
        #visited = [];

        sum = 0;
        weightedpaths = [];
        forall @edges as e
        {
            if(e->pheromone==0)
            {
                insert(weightedpaths,0.1,len(weightedpaths)-1);
                sum += 0.1; 
            }
            else
            {
                insert(weightedpaths,e->pheromone,len(weightedpaths)-1);
                sum += e->pheromone;
            }
        }
        itr=0;
        edgesAmount = len(@edges);
        while(itr << edgesAmount)
        {
            if( rand([0,1]) << weightedpaths[itr]/sum)
            {
                #destination = @edges[itr]->to;
            }
            itr+=1;
            on:arrive
            {
                if(@state == 'goal')
                {
                    #state = backtrackwithpheremone;
                    add(#visited,next,len(#visited)-1);
                }
                send @ant;
            }
        }
    }
}
"""
# -----------------------------------------
"""

<< Boolean_Curcuit >>
{
    <base>
    {
        signal = msg;
        signal->sign = @input_val;
        send signal;
    }
    <receive signal in and>
    {
        inter_output = msg;
        inter_output->data = true;
        
        forall @queue as s
        {
            inter_output->data = inter_output->data & s->signal->sign;
        }

        send inter_output;
    }
    <receive signal in or>
    {
        inter_output = msg;
        inter_output->data = true;
        
        forall @queue as s
        {
            inter_output->data = inter_output->data | s->signal->sign;
        }

        send inter_output;
    }
    <receive signal in not>
    {
        inter_output = msg;
        inter_output->data = true;
        
        inter_output->data  = !s->signal->sign;

        send inter_output;
    }
    <receive signal in output>
    {
        log signal->data;
    }
}
"""


"""
<< Kuromato_Model >>
{
    <base>
    {
        pulse = msg;
        pulse->data = {'theta':@theta};

        log @theta;

        send pulse;
    }
    < receive pulse >
    {
        sum = @nat_freq;
        forall @queue as p
        {
            sum += sin(pulse->data['theta'] - @theta);
        }
        /*potentially wrong updating method, may need euler or ode45 to run*/
        @theta = (@k/@total_nodes)*sum*delta_t + @theta;

        @state = 'base';
    }
}
"""
