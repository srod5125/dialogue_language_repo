import networkx as nx
from lark import Lark


class DialogueLang():
    def __init__(self, text):
        self.text = text
        self.parser = Lark(r"""
            ?start : exchange_blocks+

            ?exchange_blocks : "<" [ordering] "throw" var ["in" state] ">" "{" (statement*|batchprocessing*) "}" -> send_msg
                            | "<" [ordering] "catch" var ["in" state] ">" "{" (statement*|batchprocessing*) "}" -> receive_msg

            ?ordering : "."

            ?batchprocessing : "valve" "(" [_seq{assignment}] ";" [conditional_expr] ";" [_seq{assignment}] ")" "{" statement+ "}" -> batch_process

            ?statement : "for" (name "=" arithmatic_expr) "to" conditional_expr "{" statement+ "}" -> for_loop
                        | "forall" name "as" var "{" statement+ "}" -> for_each_loop
                        | "if" conditional_expr "{" statement+ "}" ( "else" "{" statement+ "}"  )* -> if_statement
                        | assignment ";"
                        | "send" name ";" -> send

            ?assignment : name "=" expr -> assign
                        | "state" "=" (name|NUMBER) -> state_assign
                        | name "=" dict
                        | name "=" list
                        | name "=" conditional_expr "?" expr ":" expr -> ternary
                        | name "+=" arithmatic_expr -> plus_equal
            
            ?expr : conditional_expr | arithmatic_expr | string_manipulation_expr

            ?conditional_expr : conditional_expr "&" rest_cond -> and_condition
                                | conditional_expr "|" rest_cond -> or_condition
                                | "!" rest_cond -> not_condition
                                | (conditional_expr "==" rest_cond | arithmatic_expr "==" arithmatic_expr ) -> equal_condition
                                | ("state" "==" var | var "==" "state") -> state_equality
                                | (conditional_expr "!=" rest_cond | arithmatic_expr "!=" arithmatic_expr ) -> unequal_condition
                                | ("state" "!=" var | var "!=" "state") -> state_unequality
                                | "(" conditional_expr ")"
                                | arithmatic_expr ">>" rest_aritmatic -> greater_than
                                | arithmatic_expr "<<" rest_aritmatic -> less_than
            ?rest_cond : conditional_expr | bool | name
            ?bool : "true" -> true | "false" -> false

            ?arithmatic_expr : "(" arithmatic_expr ")"
                                | arithmatic_expr "-" rest_aritmatic -> sub
                                | arithmatic_expr "*" rest_aritmatic -> mul
                                | arithmatic_expr "/" rest_aritmatic -> div
                                | arithmatic_expr "+" rest_aritmatic -> add 
                                | rest_aritmatic
            ?rest_aritmatic : arithmatic_expr | NUMBER | name | "delta_t" -> tick

            ?string_manipulation_expr : string_manipulation_expr "+" rest_string -> string_add
                                        | rest_string
            ?rest_string : string_manipulation_expr | ESCAPED_STRING | name | "current_state" -> get_current_state

            
            ?name:  var | property | dict_value | list_val
            ?var: WORD | CNAME
            ?dict_value : var "[[" (arithmatic_expr|name|string_manipulation_expr)  "]]" -> dict_access
            ?list_val : var "[" (arithmatic_expr)  "]" -> list_access
            ?property: var "->" name -> property_var
                        | "to" "->" name -> msg_to
                        | "data" "->" name -> msg_data
                        | "sender" "->" name -> msg_sender
                        | "path" "->" name -> msg_path

            ?dict : "{" [ (NUMBER|ESCAPED_STRING|name) ":" (NUMBER|ESCAPED_STRING|name|bool|dict) ( "," (NUMBER|ESCAPED_STRING|name) ":" (NUMBER|ESCAPED_STRING|name|bool|dict) )* ] "}"
            ?list : "[" [   (NUMBER|ESCAPED_STRING|name|bool|dict|list) ( "," (NUMBER|ESCAPED_STRING|name|bool|dict|list) )*    ] "]"
            
            ?state: var|NUMBER

            _seq{val}: val ("," val)* 

            %import common.ESCAPED_STRING
            %import common.WORD
            %import common.CNAME
            %import common.NUMBER
            %import common.WS
            %import common.C_COMMENT

            %ignore WS
            %ignore C_COMMENT
            """, start='start')


# --------TO_DO--------
# output, user input
# processing received messages
# where and how messages travel, the throw specifies how a message travels
# neighbor memory access
# prevent batch processing from happening in a throw block

# implmementing neigbor broadcasting only, throw msg => catch msg -> send msg format
#                                   sends the same message
#                                    path variable is updated with current state and
#                                   id of node traversed

# block access to sender by saying if response->state != somestate, msg always includes state and id of caught msg
#
# queue batch processing model for catches, yeild processing or conditional queue breaks and plays

# movie controls for recording and timing recordings of data: clock = 0.1, record 5-19s
# importing graph types
# wrappers for showcasing on matplot lib


if __name__ == '__main__':
    data = """
            <throw requestState>
            {
                send request;
            }
            <catch request>
            {
                response->data = {"state":current_state};
                send response ;
            }
            <catch response>
            {
                valve (sum = 0;clock == 4;)
                {
                    if response->data[["state"]] == ALIVE
                    {
                        sum += 1;
                    }
                }
                
            }
            """
    d_lang = DialogueLang(data)
    print(d_lang.parser.parse(data).pretty())


"""
::
:?  response->data["state"] == ALIVE
:> 



            <catch request>
            {
                response->data = {"state":current_state}
                send response
            }
            <catch response>
            {
                response->data["state"] = ALIVE
            }
"""
