"""
Set of decorators for model data presentation
"""
def data_func(method):
    method.data_func = True
    return method
