import sqlglot
from sqlalchemy import create_engine, text, MetaData


class SQLValidator:
    def __init__(self, db_path="db/soil_pollution.db", allowed_tables=None):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.schema_tables = set(allowed_tables or [])
        self.schema_columns = set()
        self._reflect_schema()
    
    def _reflect_schema(self):
        metadata = MetaData()
        metadata.reflect(self.engine)
        self.schema_tables = {t.name for t in metadata.tables.values()}
        self.schema_columns = {c.name for t in metadata.tables.values() 
                              for c in t.columns}
    
    def safety_check(self, sql):
        try:
            parsed = sqlglot.parse(sql, dialect='sqlite')
            if not parsed:
                return False, "Unsafe: Parse failed - empty result"
            
            parsed_ast = parsed[0]
            
            # Block DDL/DML
            ddl_nodes = [sqlglot.exp.Drop, sqlglot.exp.Create, sqlglot.exp.Alter,
                        sqlglot.exp.Truncate, sqlglot.exp.Rename]
            dml_nodes = [sqlglot.exp.Delete, sqlglot.exp.Insert, sqlglot.exp.Update]
            
            for node_type in ddl_nodes + dml_nodes:
                if parsed_ast.find(node_type):
                    return False, f"Unsafe: {node_type.__name__} operation detected"
            
            if not isinstance(parsed_ast, sqlglot.exp.Select):
                return False, "Unsafe: Non-SELECT statement"
            
            return True, "Safe - SELECT only"
        except Exception as e:
            sql_upper = sql.upper()
            harmful_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER']
            if any(keyword in sql_upper for keyword in harmful_keywords):
                return False, "Unsafe: Harmful keyword detected"
            return True, "Safe - Keyword check passed"
    
    def _collect_aliases_from_select(self, select_node):
        """Collect all column aliases from a SELECT node."""
        aliases = set()
        if isinstance(select_node, sqlglot.exp.Select):
            for expr in select_node.expressions:
                if expr.alias:
                    aliases.add(expr.alias)
        return aliases
    
    def semantic_check(self, sql):
        """Validate ONLY real columns, exclude aliases, CTEs, and derived columns."""
        try:
            parsed = sqlglot.parse(sql, dialect='sqlite')
            if not parsed:
                return False, "Semantic: Parse failed"
            
            parsed_ast = parsed[0]
            
            # Collect CTE names and their output columns
            cte_names = set()
            cte_columns = set()
            
            for cte in parsed_ast.find_all(sqlglot.exp.CTE):
                if cte.alias:
                    cte_names.add(cte.alias)
                    # Collect columns defined in this CTE
                    cte_select = cte.this
                    cte_columns.update(self._collect_aliases_from_select(cte_select))
            
            # Collect all aliases from all SELECT clauses (including subqueries)
            all_select_aliases = set()
            for select_node in parsed_ast.find_all(sqlglot.exp.Select):
                all_select_aliases.update(self._collect_aliases_from_select(select_node))
            
            # Extract REAL columns (exclude aliases, CTE columns, and derived columns)
            real_columns = set()
            for column in parsed_ast.find_all(sqlglot.exp.Column):
                col_name = column.name
                
                # Skip if this is a SELECT alias or CTE column
                if col_name in all_select_aliases or col_name in cte_columns:
                    continue
                
                # Skip if column itself has an alias definition
                if column.alias:
                    continue
                
                # Skip if column is part of an alias definition
                if column.find_ancestor(sqlglot.exp.Alias):
                    continue
                    
                real_columns.add(col_name)
            
            # Extract used tables, excluding CTEs
            used_tables = {t.name for t in parsed_ast.find_all(sqlglot.exp.Table)}
            used_tables = used_tables - cte_names
            
            missing_tables = used_tables - self.schema_tables
            missing_columns = real_columns - self.schema_columns
            
            if missing_tables:
                return False, f"Missing tables: {missing_tables}"
            if missing_columns:
                return False, f"Missing columns: {missing_columns}"
            return True, "Schema valid"
        except Exception as e:
            return False, f"Semantic error: {str(e)}"
    
    def execution_check(self, sql):
        try:
            with self.engine.begin() as conn:
                conn.execute(text(sql))
            return True, "Executed successfully"
        except Exception as e:
            return False, f"Runtime error: {str(e)}"
    
    def validate(self, sql):
        checks = [
            ("Safety", self.safety_check(sql)),
            ("Semantic", self.semantic_check(sql)),
            ("Execution", self.execution_check(sql))
        ]
        
        for stage, (ok, msg) in checks:
            if not ok:
                return False, f"{stage} failed: {msg}"
        return True, "All validations passed"