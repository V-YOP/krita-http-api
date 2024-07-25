from typing import Any, Union, List, Tuple, Optional

class ValidationError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__()
        self.msg = msg
    pass

def json_validate(value: Any, expected_type: Any, path: str = "") -> None:
    """
    json validator, use user-defined shape (typescript-like) to validate json value

    shape example:
    ```
    {
        'code': int, # int
        'datas': [str], # string[]
        'param': Nullable({ # T | null 
            'anyObject': {}, # any object
            'literal': {'hello', 'world'}, # 'hello' | 'world'
            'coord': (int, Nullable(int)), # [int, int | None]
            'arrayObjects': [{ 'name': str, 'age': int }] # {name: string, age: int}[]
        })
    }
    ```

    """
    if isinstance(expected_type, list):
        if not isinstance(value, list):
            raise ValidationError(f"Field '{path}' required 'list', got '{type(value).__name__}'")
        element_type = expected_type[0]
        for index, item in enumerate(value):
            json_validate(item, element_type, f"{path}[{index}]")
    elif isinstance(expected_type, tuple) and expected_type[0] == "nullable":
        if value is not None:
            json_validate(value, expected_type[1], path)
    elif isinstance(expected_type, tuple):
        if not isinstance(value, list) or len(value) != len(expected_type):
            raise ValidationError(f"Field '{path}' required 'tuple of {len(expected_type)} elements', got '{value}'")
        for index, (item, exp_type) in enumerate(zip(value, expected_type)):
            json_validate(item, exp_type, f"{path}[{index}]")
    elif isinstance(expected_type, set):
        if value not in expected_type:
            raise ValidationError(f"Field '{path}' required one of '{expected_type}', got '{value}'")
    elif isinstance(expected_type, dict):
        if not isinstance(value, dict):
            raise ValidationError(f"Field '{path}' required 'dict', got '{type(value).__name__}'")
        for key, exp_type in expected_type.items():
            if key in value:
                json_validate(value[key], exp_type, f"{path}.{key}" if path else key)
            else:
                json_validate(None, exp_type, f"{path}.{key}" if path else key)
        for key in value.keys():
            if key not in expected_type:
                raise ValidationError(f"Field '{path}' need no field '{key}'. valid keys: {list(expected_type.keys())}")

    elif isinstance(expected_type, type):
        if expected_type == float: # let float can accept int
            expected_type = (int, float)
            if not isinstance(value, expected_type):
                raise ValidationError(f"Field '{path}' required '{float.__name__}', got '{type(value).__name__}'")
        if not isinstance(value, expected_type):
            raise ValidationError(f"Field '{path}' required '{expected_type.__name__}', got '{type(value).__name__}'")
    else:
        raise ValidationError(f"Unknown type for field '{path}': {expected_type}")


def Nullable(element_type: type) -> Tuple[str, type]:
    return "nullable", element_type

def json_validate_p(value: Any, expected_type: Any):
    try:
        json_validate(value, expected_type)
        return True
    except:
        return False
    

# def shape(expected_type: Any) -> str:
#     def go(expected_type, path='') -> str:
#         if isinstance(expected_type, list):
#             return f"{go(expected_type[0], f"{path}[]")}[]"
#         elif isinstance(expected_type, tuple) and expected_type[0] == "nullable":
#             return f"Optional<{go(expected_type[1], path)}>"
#             # raise ValidationError(f"Field '{path}' required '{expected_type[1].__name__} or null', got '{type(value).__name__}'")
        
#         elif isinstance(expected_type, tuple):
#             res = []
#             for i, field_type in enumerate(expected_type):
#                 res.append(go(field_type, f"{path}[i]"))
#             return '[' + ', '.join(res) + ']'
        
#         elif isinstance(expected_type, set):
#             res = []
#             for i, field_type in enumerate(expected_type):
#                 res.append(go(field_type, f"{path}[i]"))
#             return '(' + ' | '.join(res) + ')'
        
#         elif isinstance(expected_type, dict):
#             res = {}
#             for key, exp_type in expected_type.items():
#                 field = go(exp_type, f"{path}.{key}")
#                 res[key] = field
#         elif isinstance(expected_type, type):
#             if not isinstance(value, expected_type):
#                 raise ValidationError(f"Field '{path}' required '{expected_type.__name__}', got '{type(value).__name__}'")
#         else:
#             raise ValidationError(f"Unknown type for field '{path}': {expected_type}")
#     pass

if __name__ == '__main__':

    #int test
    assert not json_validate_p(1, float)
    assert json_validate_p(1, int)

    #bool test
    assert not json_validate_p(True, float)
    assert json_validate_p(True, bool)
    # bool is a int, LMAO
    assert json_validate_p(True, int)

    # string test
    assert not json_validate_p('hello', int)
    assert json_validate_p('hello', str)

    # literal test
    assert not json_validate_p('hello', {'wo11', 'world'})
    assert json_validate_p('hello', {'hello', 'world'})

    # Nullable test
    assert not json_validate_p('hello', Nullable(int))
    assert json_validate_p(1, Nullable(int))
    assert json_validate_p(None, Nullable(int))
    
    assert json_validate_p(None, Nullable({}))
    assert json_validate_p({'param': 1}, Nullable({'param': int}))
    assert not json_validate_p({'param': 'hello'}, Nullable({'param': int}))
    assert json_validate_p({'param': 1}, Nullable({'param': Nullable(int)}))
    assert json_validate_p({'param': None}, Nullable({'param': Nullable(int)}))
    assert json_validate_p({}, Nullable({'param': Nullable(int)}))

    # list test
    assert not json_validate_p([2.00], [int])
    assert json_validate_p([2], [int])
    assert json_validate_p([], [{'name': str, 'age': int}])
    assert json_validate_p([dict(name='amami haruka',age=17),dict(name='chihaya',age=17)], [{'name': str, 'age': int}])
    assert not json_validate_p([dict(name='amami haruka',age='17'),dict(name='chihaya',age=17)], [{'name': str, 'age': int}])

    # tuple test
    assert json_validate_p([1,2,3], (int,int,int))
    assert json_validate_p([1,2,None], (int,int,Nullable(int)))
    assert json_validate_p([1,2,3], (int,int,Nullable(int)))

    # dict test
    assert json_validate_p({'a': 1, 'b': 2}, dict)



# Example usage
TYPE_DEF = {
    'code': str,
    'param': {
        'status': {'hel1lo'}
    }
}

user_input_object = {
    'code': 'example',
    'param': {
        'data': ['a', 'b', 'c'],
        'pos': [1, 2],
        'id': None,
        'status': 'hello'
    }
}

try:
    # json_validate(user_input_object, TYPE_DEF)
    print("Validation passed!")
except ValidationError as e:
    print(e)
