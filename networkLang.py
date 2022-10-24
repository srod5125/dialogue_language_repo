import networkx as nx
from lark import Lark


class ProtoolLanguage():
    def __init__(self, text):
        self.text = text
        self.parser = Lark(r"""
            ?start : time+ block*
            ?time : "clock" (FLOAT|NUMBER) ";" -> clock
                    | "message_rates" [name] (FLOAT|NUMBER) ";" -> message_rate
            
            ?block : header "<<" content ">>"

            ?header : name ":" level -> hdr
            ?level : ("0"|"edge") -> msg 
                        | ("1"|"node") -> nodes

            ?content : ( "state" ":" (name|NUMBER)  "(" statement+ ")" )+ -> state_block
                        | statement+
            
            ?statement : "for" assignment "to" conditional "(" (statement)+ ")" -> for_loop
                        | "forall" (name|packages) "as" name "(" (statement)+ ")" -> for_each_loop
                        | "if" conditional "(" (statement)+ ")" ( "else" "(" (statement)+ ")"  )* -> if_statement
                        | state "=" (name|NUMBER) -> state_assign
                        | assignment | primitive | handler
            

            ?primitive : "request" "{" "@" "data" dict  [ "@" "selector" "(" conditional ")"]  "}"  "->" (name|handler) -> request_msg
                        | "broadcast" "{" ["@" "data" dict ]  [ "@" "selector" "(" conditional ")"]  "}" "->" (name|handler) -> broadcast_msg
                        | "onsend"  "{" statement+ "}"  ->  on_send_msg
                        | "onarrival" "{" statement+ "}" -> on_arrival_msg
                        | "enroute" "{" statement+ "}" -> enroute_msg
                        
            ?handler : "->" name "(" statement+ ")" -> hndlr
        
        
            ?assignment : name "=" (expr|value) -> assign

            ?conditional : "not" "(" expr ")" -> not_condition
                        | (_binopparen{"or",expr} | _binop{"or",expr}) -> or_condition
                        | (_binopparen{"and",expr} | _binop{"and",expr})  -> and_condition
                        | (_binopparen{">",expr} | _binop{">",expr}) -> greater_condition
                        | (_binopparen{"<",expr} | _binop{"<",expr} )-> less_condition
                        | (_binopparen{"==",expr} | _binop{"==",expr}) -> equal_condition
            
            ?expr :  conditional
                        | expr "+" rest -> add
                        | expr "-" rest -> sub
                        | expr "*" rest -> mul
                        | expr "/" rest -> div
                        | rest

            ?rest :  expr | value
            ?value : NUMBER | FLOAT | name | ESCAPED_STRING | list | dict | packages

            ?list :  "[" [_seq{value}] "]" [ "[" (name|expr)  "]" ]
            ?dict : "{" [ (NUMBER | FLOAT | name | ESCAPED_STRING) ":" (value|state) ("," (NUMBER | FLOAT | name | ESCAPED_STRING) ":" (value|state) )* ]  "}" 



            ?name : (WORD|CNAME) [ "[" (name|expr)  "]" ]
            ?state : "current_state" -> my_state
            ?packages : "data" [ "[" (name|expr)  "]" ] -> pkgs

            _binopparen{op, line}: "(" line ")" op "(" line ")"
            _binop{op, line}: line op line 
            _seq{val}: val ("," val)* 
            


            %import common.ESCAPED_STRING
            %import common.WORD
            %import common.CNAME
            %import common.NUMBER
            %import common.FLOAT
            %import common.WS
            %import common.C_COMMENT

            %ignore WS
            %ignore C_COMMENT
            """, start='start')


# TO DO
# -------- high priority -----------
# expressability examples, further verify parser
# interface with graph primitives
# output stream, print, wrappers for plt animations
# -------- ------------- -----------
# function creation outside blocks, can be acessed by all instances
# g_variablename, for global acess as in every node or msg, or simplayer will have a instance of that variable
# transition table
# acessing message strucutre


# anticipated error : expresions arent typed so expect type errors

# _optionalParen{line}: ( "(" line ")" | line)
# get balanced parenthiess in expressions and conditionals


if __name__ == '__main__':
    data = """
            clock 1.0;
            cell:node
            <<
                state:alive
                (
                    request { 
                        @ data { "state" : current_state}
                        } -> handleAilve
                )
                
                -> handleAilve
                (
                    /* broadcast send back to receiver, handle ailve has acess to data not broadcast,
                    must be passed as parameter  */
                    
                    broadcast { ["@" "data" dict ]  [ "@" "selector" "(" conditional ")"]  } "->" (name|handler)
                )
            >>
            """
    protoclLang = ProtoolLanguage(data)
    #ip = protoclLang.parse_interactive(data)
    # print(ip.accepts())
    print(protoclLang.parser.parse(data).pretty())

"""
            clock 1.0;
            cell:node
            <<
                state:0
                (
                    for x=1 to 10>x or x==10
                    (
                        p = 1+1+[1,2,3]
                        request{xyz;} @ handle123
                    )
                    -> handle123
                    (
                        x=1
                    )
                )
            >>
            """


"""

sumOfAlive = 0

                    forall data as packages
                    (
                        if packages["state"] == alive
                        (
                            sumOfAlive = sumOfAlive + 1
                        )
                    )


"""
