syncsets = {
    # TODO: Add / Edit / Delete from this list as needed, try out!!!
    'parseProgram'                  :['tc_EOF'],
    'parseIdentifierList'           :['tc_RPAREN','tc_COLON','tc_SEMICOL'],
    'parseDeclarations'             :['tc_FUNCTION','tc_PROCEDURE','tc_BEGIN','tc_SEMICOL'],
    'parseType'                     :['tc_SEMICOL','tc_VAR','tc_FUNCTION','tc_PROCEDURE'],
    'parseSubprogramDeclarations'   :['tc_BEGIN','tc_SEMICOL'],
    'parseSubProgramHead'           :['tc_SEMICOL','tc_VAR','tc_BEGIN'],
    'parseArguments'                :['tc_COLON','tc_SEMICOL'],
    'parseParameterList'            :['tc_RPAREN','tc_COLON','tc_SEMICOL'],
    'parseCompoundStatement'        :['tc_DOT','tc_SEMICOL','tc_END','tc_BEGIN'],
    'parseStatementList'            :['tc_END'],
    'parseStatement'                :[],
    'parseVariable'                 :['tc_ASSIGNOP','tc_ADDOP','tc_MULOP','tc_ID','tc_NUM','tc_LPAREN','tc_RPAREN','tc_NOT'],
    'parseProcedureStatement'       :['tc_SEMICOL','tc_END'],
    'parseExpressionList'           :['tc_RPAREN'],
    'parseSimpleExpression'         :['tc_RELOP'],
    'parseTerm'                     :['tc_ADDOP'],
    'parseFactor'                   :[]
}